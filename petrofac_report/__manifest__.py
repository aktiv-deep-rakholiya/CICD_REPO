# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Petrofac Report',
    'version': '18.0.1.0.0',
    'summary': 'Petrofac Report',
    'description': """
          Petrofac Report
           """,
    'author': 'Aktiv Software',
    'website': 'www.aktivsoftware.com',
    'depends': ['project_management', 'project_petrofac', 'enquiry_module' ,'prime4_report'],
    'data': [
        'security/ir.model.access.csv',
        'views/ace_plantech_report_view.xml',
        'views/applus_velosi_summary_report_view.xml',
        'views/eneico_report_view.xml',
        'views/global_scs_report_view.xml',
        'views/neil_barnett_report_view.xml',
        'views/petrofac_bureau_summary_report_view.xml',
        'views/petrofac_enzone_summary_report_view.xml',
        'views/petrofac_turk_summary_report_view.xml',
        # 'views/petrofac_koc_summary_report_view.xml',
        # 'views/petrofac_qusahwise_summary_report_view.xml',
        # 'views/petrofac_majnoon_summary_report_view.xml',
        # 'views/edif_nde_report_view.xml',
        # 'views/petrofac_tinhert_summary_report_view.xml',
        # 'views/petrofac_ain_tsila_summary_report_view.xml',
        # 'views/jk_inspection_report_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': "OPL-1"
}
