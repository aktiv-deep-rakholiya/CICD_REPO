# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Enquiry',
    'version': '18.0.1.0.0',
    'category': 'Project Enquiry',
    'summary': 'Project Enquiry',
    'description': """ Project Enquiry""",
    'author': 'Aktiv Software',
    'website': 'www.aktivsoftware.com',
    'depends': ['base','project_management','p4_purchase_order_10'],
    'data': [
        "security/ir.model.access.csv",
        "wizard/lost_wizard_views.xml",
        "views/project_enquiry_views.xml",
        "views/calendar_event_views.xml",
        "views/project_management_views.xml",
        "views/purchase_order_views.xml",
        "data/sequence.xml",
        "data/ir_cron.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': "OPL-1"
}
