# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Prime4 Report',
    'version': '18.0.1.0.0',
    'summary': 'Prime4 Report',
    'description': """
            Prime4 Report
           """,
    'author': 'Aktiv Software',
    'website': 'www.aktivsoftware.com',
    'depends': ['project_management','enquiry_module','project_petrofac'],
    'data': [
        'security/ir.model.access.csv',
        'views/timesheet_summary_report_view.xml',
        'views/visit_summary_report_view.xml',
        'views/visit_summary_report2_view.xml',
        'views/al_general_report_view.xml',
        'views/monarch_style_report_view.xml',
        'views/tecnicas_reunidas_report_view.xml',
        'views/tecnicas_reunidas_bapco_report_view.xml',
        # 'views/stamicarbon_report_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': "OPL-1"

}

