 #-*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError



class plazos(models.Model):
    _inherit = 'account.payment.term'
    
    tiempoPago = fields.Selection([('1', 'Inmediato'),('2', 'Plazo'),('3', 'Mixto')],string='Clasificación DGI', default='1', help='Clasificación del Plazo de pago de accuerdo a la DGI')

#descuentBonificacion =dict(descDescuento="descuentos", montoDescuento =20)


class totaliza(models.Model):
    _inherit = "facturas_electronicas.facturas_electronicas"
    
    def lista_descuentos_dict(self):
        pass
    

    def lista_plazo_dict(self, toma_fecha):
        result1=[]
        factura_objeto=self.env['account.move'].sudo().search([('name','=', self.name)])
        fecha_vencimiento_factura = factura_objeto.invoice_date_due
        total = self.valorTotal 
        offset = factura_objeto.user_id.tz_offset
        lista_pagos=[]
        if toma_fecha:
            fecha_vencimiento = fecha_vencimiento_factura
            cuota = "{0:.2f}".format(total)
            salida=dict()
            salida['fechaVenceCuota'] = fecha_vencimiento.strftime("%Y-%m-%dT%H:%M:%S") + offset[0:3] + ':' + offset[3:5]
            salida['valorCuota'] = cuota
            result1.append(salida)
        else:
            plazos  = self.env['account.move'].sudo().search([('name','=',self.name)]).invoice_payment_term_id.line_ids
            pago_1 = 0
            for plazo in plazos:
                dias = plazo.days
                valor = plazo.value
                salida=dict()
                fecha_vencimiento = factura_objeto.create_date + timedelta(days=dias)
                if  valor == 'balance':
                    cuota = "{0:.2f}".format(total - pago_1)
                elif valor == 'percent':
                    cuota = "{0:.2f}".format(total * (plazo.value_amount/100))
                elif valor == 'fixed' :
                    cuota = "{0:.2f}".format(plazo.value_amount)
                pago_1 = float(cuota)
                salida['fechaVenceCuota'] = fecha_vencimiento.strftime("%Y-%m-%dT%H:%M:%S") + offset[0:3] + ':' + offset[3:5]
                salida['valorCuota'] = cuota
            #salida['infoPagoCuota'] = "Cuota pago" 
                result1.append(salida)
                pago = {"formaPagoFact": "02",
                        "descFormaPago": " ",
                        "valorCuotaPagada": cuota
                       }
                lista_pagos.append(pago)
        result=dict(
        pagoPlazo = result1
        )
        return (result,lista_pagos)
    
    
    def formaPago_dict(self):
        result=dict(
        formaPago=[
        {"formaPagoFact": "02",
        "descFormaPago": " ",
        "valorCuotaPagada": "{0:.2f}".format(self.valorTotal)
        }
        ]
        )
        return result

    def formaPago_Plazo_dict(self, lista_pagos):
        
        lista = []
        if len(lista_pagos) == 0:
           salida = {"formaPagoFact": "02",
        "descFormaPago": " ",
        "valorCuotaPagada": "{0:.2f}".format(self.valorTotal)
        }
        
           lista.append(salida) 
        else:
           lista = lista_pagos
        result=dict(
        formaPago=lista
        )
        return result
    
    
    
    def totales_dict(self):
        factura_objeto=self.env['account.move'].sudo().search([('name','=', self.name)])
        
        tiempo_pago = factura_objeto.invoice_payment_term_id.tiempoPago
        fecha_vencimiento = factura_objeto.invoice_date_due
        fecha_factura = factura_objeto.invoice_date
        
        result=dict()
        
        result["totalPrecioNeto"] = "{0:.2f}".format(self.totalPrecioNeto)
        result["totalITBMS"] = "{0:.2f}".format(self.totalITBMS)
        result["totalMontoGravado"] =  "{0:.2f}".format(self.totalITBMS) #se asume ISC cero
        result["totalDescuento"] = "{0:.2f}".format(self.totalDescuento)
        #result["totalAcarreoCobrado"] = ""
        #result["valorSeguroCobrado"] = ""
        result["totalFactura"] = "{0:.2f}".format(self.valorTotal)
        result["totalValorRecibido"] = "{0:.2f}".format(self.valorTotal)
        result["vuelto"] = "0.00"
        result["nroItems"] = self.nroItems
        result["totalTodosItems"] = "{0:.2f}".format(self.totalTodosItems)
        result['listaFormaPago'] = self.formaPago_dict()
        if tiempo_pago:
            result["tiempoPago"] = tiempo_pago
            if tiempo_pago !='1' :
              result['listaPagoPlazo'] = self.lista_plazo_dict(False)[0]
        elif fecha_factura == fecha_vencimiento:
            result["tiempoPago"] = '1'
        elif fecha_factura < fecha_vencimiento:
            result["tiempoPago"] = '2'
            result['listaPagoPlazo'] = self.lista_plazo_dict(True)[0]
        result['listaFormaPago'] = self.formaPago_Plazo_dict(self.lista_plazo_dict(False)[1])    
        if self.totalDescuento: #emitir lista bonificaciones
           result['listaDescBonificacion'] ={'descuentoBonificacion':
                                              [{'descDescuento': 'Descuento',
                                                'montoDescuento' : "{0:.2f}".format(self.totalDescuento)
                                               }]
                                             }                                            
        #   result['']['descDescuento'] = 'Descuento'
        #   result['']['montoDescuento'] = "{0:.2f}".format(self.totalDescuento)
        return result





    '''
totalesSubTotales=dict({
        "totalPrecioNeto": "{0:.2f}".format(self.totalPrecioNeto),
        "totalITBMS": "{0:.2f}".format(self.totalITBMS),
        "totalMontoGravado":  "{0:.2f}".format(self.totalITBMS), #se asume ISC cero
        "totalDescuento": "",
        "totalAcarreoCobrado": "",
        "valorSeguroCobrado": "",
        "totalFactura": "{0:.2f}".format(self.valorTotal),
        "totalValorRecibido": "{0:.2f}".format(self.valorTotal),
        "vuelto": "0.00",
        #"tiempoPago": "1",
         "tiempoPago": factura_objeto.invoice_payment_term_id.tiempoPago,
        "nroItems": self.nroItems,
        "totalTodosItems": "{0:.2f}".format(self.totalTodosItems)},
        listaFormaPago=dict(
        formaPago=[
        {"formaPagoFact": "02",
        "descFormaPago": " ",
        "valorCuotaPagada": "{0:.2f}".format(self.valorTotal)
        }
        ]
        )
        )#,
                    <ser1:listaDescBonificacion>
                        <ser1:descuentoBonificacion>
                            <ser1:descDescuento>?</ser1:descDescuento>
                            <ser1:montoDescuento>?</ser1:montoDescuento>
                        </ser1:descuentoBonificacion>
                    </ser1:listaDescBonificacion>
                    <ser1:listaFormaPago>
                        <ser1:formaPago>
                            <ser1:formaPagoFact>?</ser1:formaPagoFact>
                            <ser1:descFormaPago>?</ser1:descFormaPago>
                            <ser1:valorCuotaPagada>?</ser1:valorCuotaPagada>
                        </ser1:formaPago>
                    </ser1:listaFormaPago>
                    <ser1:retencion>
                        <ser1:codigoRetencion>?</ser1:codigoRetencion>
                        <ser1:montoRetencion>?</ser1:montoRetencion>
                    </ser1:retencion>
                    <ser1:listaPagoPlazo>
                        <ser1:pagoPlazo>
                            <ser1:fechaVenceCuota>?</ser1:fechaVenceCuota>
                            <ser1:valorCuota>?</ser1:valorCuota>
                            <ser1:infoPagoCuota>?</ser1:infoPagoCuota>
                        </ser1:pagoPlazo>
                    </ser1:listaPagoPlazo>
                    <ser1:listaTotalOTI>
                        <ser1:totalOti>
                            <ser1:codigoTotalOTI>?</ser1:codigoTotalOTI>
                            <ser1:valorTotalOTI>?</ser1:valorTotalOTI>
                        </ser1:totalOti>
                    </ser1:listaTotalOTI>
                    
                    
              <ser:listaPagoPlazo>
                  <ser:pagoPlazo>
                     <ser:fechaVenceCuota>2020-12-29T08:28:28-05:00</ser:fechaVenceCuota>
                     <ser:valorCuota>5.94</ser:valorCuota>
                  </ser:pagoPlazo>
               </ser:listaPagoPlazo>  
    '''