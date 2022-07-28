 #-*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from odoo.exceptions import UserError, ValidationError
import json
import zeep
import pytz




class facturas_electronicas(models.Model):
    
    
     _name = 'facturas_electronicas.facturas_electronicas'
     _description = 'facturas_electronicas.facturas_electronicas'
    
     doc_id = fields.Many2one('account.move', readonly=True,
        string='Doc_ID')

     name = fields.Char(string='Numero' ,readonly = True)
     numdocumento = fields.Char(string='Documento',comodel_name='account.move', related ='name')
     enviado = fields.Boolean(string='Enviado', default=False, readonly = True)
     invoice_partner_display_name =  fields.Char(string='Cliente' ,readonly = True)
     partner_id = fields.Char()  
     type_name = fields.Char(string='Tipo Documento',readonly = True)
     invoice_date = fields.Char(string='Fecha',readonly = True)
     state = fields.Char(string='Status' ,readonly = True)
     amount_total = fields.Float(string='Monto',readonly = True)
     fechaSalida = fields.Char(string='Fecha de Salida',readonly = True)
     invoice_line_ids = fields.Char(string='Lineas Factura')
     amount_untaxed = fields.Char(string='Precio Neto',readonly = True)
     amount_tax = fields.Float(string='Monto Gravado',readonly = True)
     RUC = fields.Char(string='RUC',readonly = True)     
     DV = fields.Char(string='DV',readonly = True)     
     invoice_user_id = fields.Char(string='invoice_user_id',readonly = True)  
     totalPrecioNeto = fields.Float(string='Total Precio Neto' ,readonly = True)  
     nroItems = fields.Integer() 
     totalITBMS = fields.Float()
     totalTodosItems = fields.Float()
     totalDescuento = fields.Float()
     valorTotal = fields.Float()
     fecha_envio_pac= fields.Datetime(string='Ultima fecha de envío')     
     aplica_entrega= fields.Boolean(string='Aplica Entrega', default=True, readonly = True)
        
     #res.config.settings
     url_prod = fields.Text('URL produccion')
     url_test = fields.Text('URL pruebas')
     proveedor_PAC = fields.Selection([('ebi', 'EBI')], default= 'ebi')
     en_produccion = fields.Boolean(string='Ambiente Producción', default= False)

    
     #campos del response  
     cufe = fields.Char(string='CUFE',readonly = True)
     qr = fields.Char(string='Código QR', readonly = True)
     fechaRecepcionDGI = fields.Char(string='Fecha Recepcion en el DGI', readonly = True)
     nroProtocoloAutorizacion = fields.Char(string='Protocolo de Autorizacion número', readonly = True)
     mensaje = fields.Char(string='Mensaje', readonly = True)
     codigo = fields.Char(string='Código', readonly = True)
     resultado = fields.Char(string='Resultado', readonly = True)
        
        
     #funciones
    
     def ajusta_correl(self,correl):
           lista  = list(correl)
           lista.reverse()
           result=[]
           for item in lista:
             if item.isdigit():
                result.append(item)
             else:
                break
           result.reverse()
           result="".join(result)
           numceros = 10 - len(result)
           result = '0' * numceros + result
 
           return result 

    
     def chequear_resultado(self, entrada,metodo='Enviar'):
            self.enviado = True
            self.mensaje = entrada['mensaje']
            self.cufe = entrada.cufe
            self.qr = entrada.qr
            self.fechaRecepcionDGI = entrada.fechaRecepcionDGI
            self.nroProtocoloAutorizacion = entrada.nroProtocoloAutorizacion
            self.resultado = entrada.resultado
            self.codigo = entrada.codigo
            self.env['facturas_electronicas.fe_log'].graba_log(self.name, self.mensaje, self.resultado, datetime.datetime.now())
            #if self.resultado !='error':
            respuesta_ok = dict(
                enviado = True,   
                codigo= entrada.codigo,
                mensaje= entrada.mensaje,
                resultado= entrada.resultado,   
                cufe = entrada.cufe,
                qr = entrada.qr,
                fechaRecepcionDGI = entrada.fechaRecepcionDGI,
                nroProtocoloAutorizacion = entrada.nroProtocoloAutorizacion,
                fecha_envio_pac = datetime.datetime.now()  )
            factura = self.env['account.move'].search([('name', '=', self.name)])
            factura.write(respuesta_ok)
        

        
     def f_enviar(self):
        #if self.resultado=='procesado':
        #   raise UserError('Ya esta factura ha sido procesada')
        lista_campos_factura =["tipoEmision",
                               "tipoDocumento",
                               "puntoFacturacionFiscal",
                               "naturalezaOperacion",
                               "tipoOperacion",
                               "destinoOperacion",
                               "formatoCAFE",
                               "entregaCAFE",
                               "envioContenedor",
                               "tipoVenta",
                               "fechaSalida",
                               "informacionInteres",
                               "write_date",
                               "company_id",
                               "invoice_user_id",
                               "autorizados",
                               "invoice_origin"]
        datos_cliente = self.env['res.partner'].busca_cliente(self.partner_id)
        self.RUC = datos_cliente["vat"]
        self.DV  = datos_cliente["digitoVerificadorRUC"]
        
        #config = self.env['res.config.settings'].serach([])[0]
        config = self.env['ir.config_parameter'].sudo()
        produccion = config.get_param('facturas_electronicas.en_produccion')
        if produccion:
          url_a_usar = config.get_param('facturas_electronicas.url_prod')
        else:
          url_a_usar = config.get_param('facturas_electronicas.url_test')
        
        #url_a_usar = 'http://demointegracion.ebi-pac.com/ws/obj/v1.0/Service.svc?singleWsdl'
        
        if not url_a_usar:
            raise UserError('Recuerde configurar las URLS desde el módulo de Contabilidad / Factura Electrónica')
        
        factura=self.env['account.move'].sudo().search_read([('name','=', self.name)], lista_campos_factura)
        factura_objeto=self.env['account.move'].sudo().search([('name','=', self.name)])
        factura=factura[0]

        #convertir fecha  de la factura usando el timezone del usuario   
        if factura['invoice_user_id']:
            id_usuario = factura['invoice_user_id'][0]    
            zona_horaria = self.env['res.users'].sudo().search_read([('id','=', id_usuario)],['tz'])  
            zona_horaria = zona_horaria[0]['tz']
            timeZ_user = pytz.timezone(zona_horaria)
            offset = datetime.datetime.now(datetime.timezone.utc).astimezone(timeZ_user).strftime('%z')
        else:
            offset = '-0500'
        fecha_factura = factura_objeto.create_date.strftime("%Y-%m-%dT%H:%M:%S") + offset[0:3] + ':' + offset[3:5] 
        #revisar
        fechaSalida = factura["fechaSalida"].strftime("%Y-%m-%dT%H:%M:%S") + offset[0:3] + ':' + offset[3:5]  if factura["fechaSalida"] else ''

        
        datos = dict(
        #tokenEmpresa="dftitvfzogbv_tfhka",
        tokenEmpresa = factura_objeto.company_id.tokenEmpresa,
        tokenPassword = factura_objeto.company_id.tokenPassword,
        #tokenPassword="Ck:5+5uDuDxf",
        documento=dict(
        codigoSucursalEmisor =  self.env['res.company'].datos_cia(factura['company_id'][0])['codigoSucursalEmisor'],    
        tipoSucursal = self.env['res.company'].datos_cia(factura['company_id'][0])['tipoSucursal'],    
        datosTransaccion=dict(
        tipoEmision = factura["tipoEmision"],
        tipoDocumento = factura["tipoDocumento"],
        #numeroDocumentoFiscal = self.name,
        numeroDocumentoFiscal = self.ajusta_correl(self.name),    
        puntoFacturacionFiscal = factura["puntoFacturacionFiscal"],
        naturalezaOperacion = factura["naturalezaOperacion"],
        tipoOperacion = factura["tipoOperacion"],
        destinoOperacion = factura["destinoOperacion"],
        formatoCAFE = factura["formatoCAFE"],
        entregaCAFE = factura["entregaCAFE"],
        envioContenedor = factura["envioContenedor"],
        procesoGeneracion = 1,
        tipoVenta = factura["tipoVenta"] if factura["tipoVenta"] else '' ,
        fechaEmision = fecha_factura,
        fechaSalida =  fechaSalida,   #agrgar con condicional
        cliente = self.env['res.partner'].cliente_dict(self.partner_id,factura["destinoOperacion"])
        ),
        listaItems=dict(
           item = self.env['account.move.line'].busca_items_factura(self.name)
        ),
            
        totalesSubTotales = self.totales_dict()
        )
        )
            
        #si la factura no tiene presupuesto no aplica la nota de entrega( notificar y preguntar)
        #la factura no debe provenir del punto de venta (pos.order) para aplicar logistica
        
        #no aplica entrega para exportacion consultar
        
        
        #no se comtempla en la version inicial (consultar)    
        
        #si viene del ecommerce user_id es False y no se proces logistica
        #nota de credito no necesita logistica solo la fcatura de venta
        if len(factura_objeto.user_id) > 0:
        
            if (factura_objeto.invoice_origin and len(self.env['pos.order'].search([('name','=', factura_objeto.invoice_origin)])) == 0) and factura_objeto.destinoOperacion =='1'  and factura_objeto.move_type == 'out_invoice':
           
               datos['documento']['infoLogistica']= self.env["stock.picking"].dict_logistica(self.name,factura['invoice_origin'])
            
              #datos['documento']['infoEntrega']= self.env["stock.picking"].dict_entrega(self.name,factura['invoice_origin'])
        

        if factura_objeto.autorizados:
           
           datos['documento']['datosTransaccion']['listaAutorizadosDescargaFEyEventos'] = factura_objeto.busca_autorizados()

        if factura_objeto.destinoOperacion =='2':
           
           datos['documento']['datosTransaccion']['datosFacturaExportacion'] = factura_objeto.dict_exportacion(self.valorTotal)
    
        if factura_objeto.tipoDocumento in ['04','05']:
           
           datos['documento']['datosTransaccion']['listaDocsFiscalReferenciados'] =''
        
           #facturas de ecommerce deben ser tartadas como factura normal a psar de tener invoice origin
        
           if factura_objeto.invoice_origin and len(factura_objeto.user_id) > 0 and factura.ref !='': 
              datos['documento']['datosTransaccion']['listaDocsFiscalReferenciados'] = dict(docFiscalReferenciado = factura_objeto.doc_referenciados_dict(True))
           else:
              datos['documento']['datosTransaccion']['listaDocsFiscalReferenciados'] = dict(docFiscalReferenciado = factura_objeto.doc_referenciados_dict())

        
        #para debug no usar en produccion
        #with open('/home/odoo/src/user/datos.txt', 'w') as temp_file:
        #    temp_file.write("%s\n" % datos)

        #wsdl = 'http://demointegracion.ebi-pac.com/ws/obj/v1.0/Service.svc?singleWsdl'
        wsdl = url_a_usar
        client = zeep.Client(wsdl=wsdl)
        response = client.service.Enviar(**datos)
        self.enviado = True
        self.fecha_envio_pac= datetime.datetime.now()
        
        #para debug no usar en produccion
        #with open('/home/odoo/src/user/respuestahoy.txt', 'w') as temp_file:
        #    temp_file.write("%s\n" % response)
        
        #grabar factura
        self.chequear_resultado(response)
        
        
    
     def f_actualizar(self):

        campos_factura=['enviado',
                        'invoice_partner_display_name',
                        'partner_id',
                        'type_name',
                        'invoice_date',
                        'state',
                        'name',
                        'amount_total',
                        'invoice_line_ids',
                        'fecha_envio_pac',
                        'amount_untaxed',
                        'amount_tax',
                        'invoice_user_id',
                        'cufe',
                        'qr',
                        'fechaRecepcionDGI',
                        'nroProtocoloAutorizacion',
                        'mensaje',
                        'codigo',
                        'resultado']
        facturas = self.env['account.move'].sudo().search_read(['|',('move_type','=','out_invoice'),('move_type','=','out_refund') ,('state','=','posted')],campos_factura)
        grabadas = self.env['facturas_electronicas.facturas_electronicas'].sudo().search([],[])
        
        if len(grabadas)>0:
            for item in grabadas:
                item.unlink()

        for fact in facturas:
             if fact['invoice_user_id']: #revisar, en website da false
               fact['invoice_user_id'] = fact['invoice_user_id'][0]
             fact['partner_id'] =   fact['partner_id'][0]
             fact['amount_untaxed'] = "{:5.3f}".format(fact['amount_untaxed'])
             self.env['facturas_electronicas.facturas_electronicas'].create(fact)
                

class doce(models.Model):
    _inherit = "account.move"

    enviado = fields.Boolean(string='Enviado', default=False, readonly = True)
    autorizados = fields.Many2many(comodel_name ='res.partner', string ="Autorizados para descarger FE")
    fecha_envio_pac = fields.Datetime()
    
    #EBI
    tipoEmision = fields.Selection([('01', 'Autorización de Uso Previa, operación normal'),
                                    ('02', 'Autorización de Uso Previa, operación en contingencia'),
                                    ('03', 'Autorización de Uso Posterior, operación normal'),
                                    ('04', 'Autorización de Uso Posterior, operación en contingencia')], string='Tipo Emisión', default='01')    
    tipoDocumento = fields.Selection([('01', 'Factura de operación interna'),
                                    ('02', 'Factura de importación'),
                                    ('03', 'Factura de exportación'),
                                    ('04', 'Nota de Crédito referente a una FE'),
                                    ('05', 'Nota de Débito referente a una FE'),
                                    ('06', 'Nota de Crédito genérica'),
                                    ('07', 'Nota de Débito genérica '), 
                                    ('08', 'Factura de Zona Franca '), 
                                    ('09', 'Reembolso')], string='Tipo Documento', default='01')
        
    fechaInicioContingencia = fields.Date(string='Fecha Inicio Contingencia') 
    motivoContingencia = fields.Char(string='Motivo Contingencia') 
    puntoFacturacionFiscal = fields.Char(string='Punto Facturación Fiscal', default = "001")
    
    naturalezaOperacion = fields.Selection([('01', 'Venta'),
                                    ('02', 'Exportación'),
                                    ('10', 'Transferencia'),
                                    ('11', 'Devolución'),
                                    ('12', 'Consignación'),
                                    ('13', 'Remesa'),
                                    ('14', 'Entrega gratuita'), 
                                    ('20', 'Compra'), 
                                    ('21', 'Reembolso')], string='Naturaleza de la Operación', default="01")
    
    tipoOperacion= fields.Selection([("1",'Salida o venta'),
                                    ("2",'Entrada o compra')], string = 'Tipo Operación', default= "1")
    
    
    destinoOperacion = fields.Selection([("1",'Panamá'),
                                    ("2",'Extranjero')], string = 'Destino Operación', default= "1")
    
    formatoCAFE = fields.Selection([("1",'Sin generacion de CAFE'),
                                    ("2",'Cinta de papel'),
                                    ("3",'Papel formato Carta')], string = 'Formato CAFE', default= "1")
    
    entregaCAFE = fields.Selection([("1",'Sin generacion de CAFE'),
                                    ("2",'CAFE entregado en papel'),
                                    ("3",'CAFE enviado en formato electronico')], string = 'Entrega CAFE', default= "1")
    
    
    
    envioContenedor = fields.Selection([("1",'Normal'),
                                    ("2",'Receptor exceptúa al emisor de la obligatoriedad de envío del contenedor')], string = 'Envio Contenedor', default= "1")
        
    
    
    tipoVenta = fields.Selection([("1",'Venta de Giro del negocio'),
                                    ("2",'Venta Activo Fijo'),
                                    ("3",'Venta de Bienes Raíces'),
                                  ("4",'Prestación de Servicio')],
                                 string = 'Tipo Venta',
                                 default= "1",
                                 help= 'Si no es venta, no informar este campo')
    fechaSalida = fields.Datetime(string='Fecha de Salida')
    informacionInteres = fields.Char(string='Informacion de interés', default='')
    
    
    
    #campos a grabar en la factura
    cufe = fields.Char(string='CUFE', readonly = True)
    qr = fields.Char(string='Código QR', readonly = True)
    fechaRecepcionDGI = fields.Char(string='Fecha Recepcion en el DGI', readonly = True)
    nroProtocoloAutorizacion = fields.Char(string='Protocolo de Autorizacion número', readonly = True)
    mensaje = fields.Char(string='Mensaje', readonly = True)
    codigo = fields.Char(string='Código', readonly = True)
    resultado = fields.Char(string='Resultado', readonly = True)
    
    def convierte_correl(self,correl):
        prefijo = correl.split('/')[0]
        lista= list(correl.split('/')[1])
        result=''
        for m in lista:
          if m.isdigit():
            result= result + m
        result= prefijo + '/' + result
        return result    

    
    def busca_autorizados(self):
        modelo = self.env['facturas_electronicas.facturas_electronicas']
        if self.autorizados:
            lista_autorizados = []
            for record in self.autorizados:
                dict_autorizado = dict(autorizadoDescargaFEyEventos = dict(
                tipoContribuyente = 2 if record.company_type =='company' else 1,
                rucReceptor = record.vat,
                digitoVerifRucReceptor = record.digitoVerificadorRUC))
                lista_autorizados.append(dict_autorizado)
            return lista_autorizados
                
    def f_send(self):
        modelo = self.env['facturas_electronicas.facturas_electronicas']
        factura = modelo.search([('name','=',self.name)])
        factura.f_enviar()
            
             
    @api.model
    def _post(self, soft=True):
        res = super(doce, self)._post(soft=soft)
        if len(self) == 1:
           modelo = self.env['facturas_electronicas.facturas_electronicas']
           modelo.f_actualizar()
           factura = modelo.search([('name','=',self.name)])
          
           #para nota de credito referente a FE con post y enviio automatica
           respuesta = dict() 
           factura_objeto=self.env['account.move'].sudo().search([('name','=', self.name)])[0]
        
           if factura_objeto.move_type == 'out_refund' and len(factura_objeto.reversed_entry_id) > 0:
                respuesta['tipoDocumento']='04' 
           
                factura_referenciada = self.env['account.move.reversal'].sudo().search([])

                if factura_referenciada[-1].refund_method =='cancel' or factura_referenciada[-1].refund_method =='modify':
                    respuesta['naturalezaOperacion']='11'
                elif factura_referenciada[-1].refund_method =='refund':
                    respuesta['naturalezaOperacion'] ='21'                                               
                factura_objeto.write(respuesta)                                                                        
           if factura_objeto.invoice_origin and factura_objeto.move_type == 'out_refund' and factura_objeto.ref !='':
               respuesta['tipoDocumento']='04' 
               #pos=self.convierte_correl(factura_objeto.invoice_origin)
               pos=factura_objeto.invoice_origin
               ncpos=self.env['pos.order'].search([('name','=', pos)])
               if factura_objeto.amount_total ==  abs(ncpos.amount_total):
                  respuesta['naturalezaOperacion']='11'
               else:
                  respuesta['naturalezaOperacion']='21'                                 
               
               factura_objeto.write(respuesta)
            
           if len(factura)>0:
              try:
                factura.f_enviar()
              except:
                return res        
        return res
    
       

