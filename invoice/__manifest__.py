{
    'name': 'Invoice',
    'version': '18.0.1.0.0',
    'category': 'Invoice',
    'summary': 'Invoice',
    'description': """ Prime Invoice""",
    'author': 'Aktiv Software',
    'website': 'www.aktivsoftware.com',
    'depends': ['base','project_management','enquiry_module'],
    'data': [
        "data/sequence.xml",
        "security/ir.model.access.csv",
        "views/price_list_views.xml",
        "views/currency_views.xml",
        "views/upload_file_views.xml",
        "views/client_details_views.xml",
        "views/invoice_views.xml",
        "views/res_configuration_setting_views.xml",
        "views/timesheet_report_views.xml",
        "views/summary_report_views.xml",
        "views/inv_report.xml",
        "views/invoice_template.xml",
        "views/invoice_template_aed.xml"
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': "OPL-1"
}
