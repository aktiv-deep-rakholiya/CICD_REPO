# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Petrofac',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Project Petrofac',
    'description': """
           Fields added in calendar.event and project.project
           """,
    'author': 'Aktiv Software',
    'website': 'www.aktivsoftware.com',
    'depends': ['base','project_management'],
    'data': [          
			'security/ir.model.access.csv',
			'security/project_security.xml',
			'views/calendar_event_views.xml',
            'views/client_initiator_views.xml',
            'views/project_project_views.xml',
            'views/hr_employee_views.xml',
            ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': "OPL-1"
}
