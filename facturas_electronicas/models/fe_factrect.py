 #-*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from odoo.exceptions import UserError, ValidationError



class Factrec(models.Model):
    _inherit = "account.move"


    def doc_referenciados_dict(self, POS =False):
        result=[]
        documento=dict()
        if not POS:
            for factura in self.reversed_entry_id:
                offset = factura.user_id.tz_offset
                documento["fechaEmisionDocFiscalReferenciado"] =  factura.create_date.strftime("%Y-%m-%dT%H:%M:%S") + offset[0:3] + ':' + offset[3:5]
                documento["cufeFEReferenciada"] = factura.cufe
                documento["nroFacturaPapel"] = '' #no se informa por ser factura electronica
                documento['nroFacturaImpFiscal'] = ''
                result.append(documento)
        else:
            my_pos=self.convierte_correl(self.invoice_origin)
            ncpos=self.env['pos.order'].search([('name','=', my_pos)])
            offset = ncpos.user_id.tz_offset
            documento["fechaEmisionDocFiscalReferenciado"] =  ncpos.create_date.strftime("%Y-%m-%dT%H:%M:%S") + offset[0:3] + ':' + offset[3:5]
            documento["cufeFEReferenciada"] = ncpos.account_move.cufe
            result.append(documento)
        return result

    
