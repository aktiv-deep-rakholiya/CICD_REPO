# -*- coding: utf-8 -*-

from odoo import fields, models, api


class EmpReport(models.Model):
    _name = 'emp.list'
    _description = "Emp Report"

    emp_id = fields.Many2one('summary.report', ondelete='cascade', index=True)
    emp_name = fields.Char("Employee")
    days = fields.Integer(string='No of Days')
    project_id = fields.Many2one('project.project', string="Project")
    add_expenses = fields.Float(string="AdditionalExp", digits=(6, 3))
    client_id = fields.Many2one('client.master')
    with_stay = fields.Boolean(string='With Stay', default=False)
    without_stay = fields.Boolean(string='Without Stay', default=False)
    overnight_expense = fields.Boolean(string="With Overnight Expense")
    calendar_ids = fields.Many2many('calendar.event', 'emp_list_calendar_event_rel', 'emp_id', 'calendar_id',
                                    string='Calendar Events', copy=False)
    partner_ids = fields.Many2many('res.partner', 'emp_list_res_partner_rel', 'emp_id', 'partner_id',
                                   string='Vendors', copy=False)
    purchase_id = fields.Many2one('purchase.order', string='Purchase', copy=False)

    @api.depends('client_id')
    def compute_client_name(self):
        for rec in self:
            if rec.client_id:
                rec.client_name = rec.client_id.client_name
            else:
                rec.client_name = False

    client_name = fields.Selection([
        ('tcm', 'Tecnimont'),
        ('petrofac', 'Petrofac'),
        ('ace', 'ACE Plantech'),
        ('eneico', 'Eneico'),
        ('edif', 'Edif NDE'),
        ('equasrl', 'Equa SRL'),
        ('lindinger', 'Lindinger USA'),
        ('spxflow', 'Dollinger Filtration Limited'),
        ('global', 'Global SCS'),
        ('tecnicas', 'Tecnicas Reunidas'),
        ('tecton', 'Tecton'),
        ('arotec', 'Arotec'),
        ('clatech', 'Clatech Consulting Co.Ltd'),
        ('sisisrl', 'SISI SRL'),
        ('stamicarbon', 'STAMICARBON'),
        ('jkinspection', 'JK Inspection Engineering co ltd'),
        ('monarch', 'Monarch Style'),
        ('inspectorunion', 'Inspectors Union Co.'),
        ('swissapproval', 'Swiss Approval Team'),
        ('neilbarnett', 'Neil Barnett Inspection Services'),
        ('applus', 'Applus Velosi'),
        ('enzone', 'Enzone'),
        ('bureau', 'BUREAU Technical Services'),
        ('unitedglobal', 'United Global'),
        ('teleios', 'Teleios Spexxa Engg and Cons'),
        ('phbweser', 'PHB Weserhutte'),
        ('apollo', 'Apollo Electromechanical Contracting LLC'),
        ('eurture', 'Eurtrue'),
        ('others', 'Others'),

    ], string='Client', compute='compute_client_name')

    country = fields.Many2one('res.country', string='Country')
    employee_role = fields.Many2one('p4.employee.role', string='Role')
    cat_location = fields.Selection([
        ('vendorfacility', 'Vendor Facility/ Loading Unloading Location'),
        ('remote', 'Remote Expediting - With Agency Tool'),
        ('remote2', 'Remote Expediting - With Third Parties Tool'),
        ('companyoffice', 'Company Office'),
    ], string='Location', readonly=False, copy=False, index=True)

    category_expenses = fields.Selection([
        ('oncall', 'OnCall'),
        ('resident1', 'Resident1'),
        ('resident2', 'Resident2'),
        ('resident3', 'Resident3'),
        ('resident4', 'Resident4'),
        ('remotemode', 'Remote mode - half day'),
    ], string='JOB Duration', readonly=False, copy=False, index=True)

    services = fields.Selection([
        ('logistics', 'Logistics'),
        ('expediting', 'Expediting & Scheduling'),
        ('inspection', 'Inspection'),
    ], string='Services', readonly=False, copy=False, index=True)

    tax_id = fields.Many2many('account.tax', string='Taxes')
