# -*- coding: utf-8 -*-
{
    'name': 'Purchase Order',
    'version': '18.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Service Agreement for Prime',
    'description': """
            Service Agreement for Prime
           """,
    'author': 'Aktiv Software',
    'website': 'www.aktivsoftware.com',
    'depends': ['purchase','project_management','web'],
    'data': [
        'reports/report_purchaseorder.xml',
        'reports/p4_purchase_order_report.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': "OPL-1"
}
