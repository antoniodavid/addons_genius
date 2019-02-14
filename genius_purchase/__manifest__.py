# -*- coding: utf-8 -*-
{
    'name':
    "Genius Compra",
    'summary':
    """Purchase Swagger Orders""",
    # 'author': "My Company",
    # 'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category':
    'Purchases',
    'version':
    '1.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'web_notify'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/genius_rest_connection_views.xml',
        'views/genius_purchase_order_views.xml',
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}