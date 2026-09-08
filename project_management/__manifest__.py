# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Management',
    'version': '18.0.1.0.3',
    'category': 'Services',
    'summary': 'Project Management',
    'description': """
           Visit Summary
           """,
    'author': 'Aktiv Software',
    'website': 'www.aktivsoftware.com',
    'depends': ['base','project','purchase','calendar','hr'],
    'data': [
            'security/project_security.xml',
			'security/ir.model.access.csv',
			'views/project_management_view.xml',
            'views/activity_description_views.xml',
            'views/client_master_views.xml',
            'views/inspector_master_views.xml',
            'views/pricelist_master_views.xml',
            'views/project_task_views.xml',
            'views/report_number_views.xml',
            'views/p4_employee_role_views.xml',
            'views/calendar_event_views.xml',
            'views/res_partner_views.xml',
            'views/common_report_views.xml'
            ],
    'assets': {
        'web.assets_backend': [
            'project_management/static/src/css/calendar_fix.css',
            'project_management/static/src/js/fullcalendar_patch.js',
            'project_management/static/src/js/calendar_form_button_patch.js',

        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': "OPL-1"
}

