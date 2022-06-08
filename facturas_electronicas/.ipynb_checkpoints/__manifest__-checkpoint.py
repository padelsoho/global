# -*- coding: utf-8 -*-
{
    'name': "Facturas Electronicas PA",

    'summary': """
        """,

    'description': """
         Integración con EBI para la generación de facturas electrónicas en Panamá.
    """,

    'author': "THAVAS",
    'website': "http://www.thavasconsultoria.com/odoo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Retail',
    'version': '15.0.1.3',

    # any module necessary for this one to work correctly
    'depends': ['base','account','contacts','sale_management','stock'],

    # always loaded
    'data': [
        'security/factura_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/product_inherited_views.xml',
        'views/invoice_inherited_view.xml',
        'views/partners_inherited_view.xml',
        'views/stock_picking_inherited_view.xml',
        'views/company_inherited_view.xml',
        'views/tax_inherited_view.xml',
        'views/payment_term_inherited_view.xml',
        'views/res_config_settings_view.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
