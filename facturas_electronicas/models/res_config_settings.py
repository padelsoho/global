# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    url_prod = fields.Text('URL produccion')
    url_test = fields.Text('URL pruebas')
    proveedor_PAC = fields.Selection([('ebi', 'EBI')], default= 'ebi')
    en_produccion = fields.Boolean(string='Ambiente Producción', default= False)
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            url_prod = self.env['ir.config_parameter'].sudo().get_param('facturas_electronicas.url_prod'),
            url_test = self.env['ir.config_parameter'].sudo().get_param('facturas_electronicas.url_test'),
            proveedor_PAC = self.env['ir.config_parameter'].sudo().get_param('facturas_electronicas.proveedor_PAC'),
            en_produccion = self.env['ir.config_parameter'].sudo().get_param('facturas_electronicas.en_produccion'),

        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        url_prod = self.url_prod or False
        url_test = self.url_test or False
        proveedor_PAC = self.proveedor_PAC or False
        en_produccion = self.en_produccion or False


        param.set_param('facturas_electronicas.url_prod', url_prod)
        param.set_param('facturas_electronicas.url_test', url_test)
        param.set_param('facturas_electronicas.proveedor_PAC', proveedor_PAC)
        param.set_param('facturas_electronicas.en_produccion', en_produccion)