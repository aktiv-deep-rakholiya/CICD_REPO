# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Zip Reports',
    'version': '18.0.1.0.3',
    'summary': 'Zip Reports',
    'description': """
       Zip report with folder hierarchy: Coordinator > Client > Initiator > Project (containing Excel files)
           """,
    'author': 'Aktiv Softwares',
    'website': 'www.aktivsoftware.com',
    'depends': ['base','project_management', 'project_petrofac'],
    'data': [
        'security/ir.model.access.csv',
        'views/zip_reports_views.xml',
        'views/tcm_pdf_report_views.xml',
        'views/turkstream_pdf_report_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': "OPL-1"
}
