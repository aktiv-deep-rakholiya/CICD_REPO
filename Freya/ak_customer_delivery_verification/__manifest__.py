# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Author: Aktiv Software.
# mail: odoo@aktivsoftware.com
# Copyright (C) 2015-Present Aktiv Software PVT. LTD.
# Contributions:
# Aktiv Software
#       - Juhi Updadhyay
#       - Zahir kagdi
#       - Yuvrajsinh Rathod
#       - Shakib Sheikh
#       - Pravin prajapati

{
    'name': 'Customer Delivery Verification',
    'version': '18.0.1.0.2',
    'summary': 'An email is sent only once when a new customer '
               'places an order via Wire Transfer or Pay After Delivery,'
               ' notifying recipients defined in General Settings. No '
               'emails are sent for existing or verified customers,'
               ' other payment methods, or after “Pay After Invoice” is'
               ' checked.',
    'category': 'Contacts',
    "author": "Aktiv Software",
    "company": "Aktiv Software",
    "website": "www.aktivsoftware.com",
    'depends': ['contacts', 'sale', 'payment'],
    'data': [
        'data/email_template_data.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/payment_provider_views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
