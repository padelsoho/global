
'''
DatosFacturaExportacion (Existe si el destino de operación es distinto a Panamá)
Tipo	Requerido	Formato	Identificador	Descripción
String	SI	AN|3	condicionesEntrega	Condiciones de entrega de acuerdo con la Tabla 1.INCOTERMS.
String	SI	AN|3	MonedaOperExportacion	Código de moneda usada para exportación, de acuerdo a la Tabla 2. Norma ISO 4217.
String	C/C	AN|5..50	monedaOperExportacionNonDef	Obligatorio si MonedaOperExportacion = ZZZ Para monedas no definidas en la Tabla 2. Norma ISO 4217.
String	C/C	N|1..11|2.4	tipoDeCambio	Para monedas diferentes al USD. Obligatorio si existe MonedaOperExportacion.
String	C/C	N|1..20|0.4	montoMonedaExtranjera	Para monedas diferentes al USD. Obligatorio si existe MonedaOperExportacion. Debe corresponder al producto de tipoDeCambio por totalFactura.
String	NO	AN|5..50	puertoEmbarque	Puerto de Embarque de la mercancía.

List<DocFiscalReferenciado> (Opcional))
Tipo	Requerido	Formato	Identificador	Descripción
String	SI	AN|25	fechaEmisionDocFiscalReferenciado	Fecha de emisión del Documento Fiscal Referenciado
String	SI	AN|66	cufeFEReferenciada	CUFE de FE referenciada. Deben ser las 66 posiciones que conforman el CUFE.
String	SI	AN|22	NroFacturaPapel	Hace referencia al número de la factura en papel.
String	NO	AN|22	NroFacturaIF	Número de factura emitida por impresora fiscal


DescuentoBonificacion (Opcional))
Tipo	Requerido	Formato	Identificador	Descripcion
String	SI	AN|..500	DescDescuento	Descripción de descuentos o bonificaciones adicionales aplicadas a la factura.
String	SI	N|1..11|2	montoDescuento	Monto de los Descuentos/Bonificaciones y otros ajustes.

List<FormaPago>
Tipo	Requerido	Formato	Identificador	Descripción
String	SI	N|2	FormaPagoFact	01:Crédito. 02:Contado. 03:Tarjeta Crédito. 04:Tarjeta Débito. 05:Tarjeta Fidelización. 06:Vale. 07:Tarjeta de Regalo. 08:Transf/Deposito cta. Bancaria 99:Otro.
String	C/C	AN|10..100	descFormaPago	Descripción de forma de pago no listada en el formato. Obligatorio si: FormaPagoFact = 99.
String	SI	N|1..11|1..2	valorCuotaPagada	Valor de la cuota pagada utilizando esta forma de pago.

Retención (cuando a la factura aplican retenciones)
Tipo	Requerido	Formato	Identificador	Descripción
String	SI	N|2	codigoRetencion	Corresponde al catálogo de objetos de retención: 1:Pago por servicio profesional al estado 100%. 2:Pago por venta de bienes/servicios al estado 50%. 3:Pago o acreditación a no domiciliado o empresa constituida en el exterior 100%. 4:Pago o acreditación por compra de bienes/servicios 50%. 7:Pago a comercio afiliado a sistema de TC/TD 50%. 8:Otros (disminución de la retención).
String	SI	N|1..11|1..2	montoRetencion	Monto de la retención a aplicar. Debe corresponder al cálculo de la retención por el objeto de retención (TasaITBMS * TotalITBMS).

List <PagoPlazo> (Opcional)
Tipo	Requerido	Formato	Identificador	Descripción
String	SI	AN|25	FechaVenceCuota	Fecha de vencimiento de la cuota.
String	SI	N|1..11|1..2	ValorCuota	Valor de la cuota.
String	NO	AN|15..1000	InfoPagoCuota	Información de interés del emisor con respeto a esta cuota.

PedidoComercialItem (Opcional)
Tipo	Requerido	Formato	Identificador	Descripción
String	SI	N|1..9	NroPedidoCompraItem	Número del pedido de compra.
String	SI	AN|1..3	NroItem	Número secuencial del ítem en el pedido.
String	NO	AB|0..5000	InfoItem	Información de interés del emisor con respeto al pedido comercial, relacionado con un ítem de la factura.

PedidoComercialGlobal (opcional)
Tipo	Requerido	Formato	Identificador	Descripción
String	SI	N|1..12	NroPedidoCompraGlobal	Número del pedido de compra.
String	C/C	AN|1..12	codigoReceptor	Permite registrar el código con que el facturador identifica a su cliente o receptor de la factura
String	C/C	AN|1..12	nroAceptacion	Numero de aceptación de la lista de números de aceptación del pedido de compra
String	C/C	A|1..50	codigoSistemaEmisor	Permite registrar el código del sistema que emite la factura electrónica.
String	C/C	AN|0..5000	InfoPedido	Información de interés del emisor con respecto al Pedido Comercial global.


ListaNroAceptacion (Opcional)
Tipo	Requerido	Formato	Identificador	Descripción
String	C/C	AN|1..12	nroAceptacion	Número de aceptación del pedido de compra



'''
