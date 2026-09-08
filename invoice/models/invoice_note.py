from odoo import models, fields ,api


class InvoiceNote(models.Model):
    _name = 'invoice.note'
    _description = "Invoice Note"

    inv_note = fields.Many2one('invoice', ondelete='cascade')
    stay = fields.Float('With Overnight Expenses', default=0.0, copy=False)
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order No')
    client_name1 = fields.Selection([
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

    ], string='Client')

    country = fields.Many2one('res.country', string='Country')
    employee_role = fields.Many2one('p4.employee.role', string='Role')

    cat_location = fields.Selection([
        ('vendorfacility', 'Vendor Facility/ Loading Unloading Location'),
        ('remote', 'Remote Expediting - With Agency Tool'),
        ('remote2', 'Remote Expediting - With Third Parties Tool'),
        ('companyoffice', 'Company Office'),
    ], string='Location', readonly=False, copy=False, index=True)

    services = fields.Selection([
        ('logistics', 'Logistics'),
        ('expediting', 'Expediting & Scheduling'),
        ('inspection', 'Inspection'),
    ], string='Services', readonly=False, copy=False, index=True)

    category_expenses = fields.Selection([
        ('oncall', 'OnCall'),
        ('resident1', 'Resident1'),
        ('resident2', 'Resident2'),
        ('resident3', 'Resident3'),
        ('resident4', 'Resident4'),
        ('remotemode', 'Remote mode - half day'),
    ], string='JOB Duration', readonly=False, copy=False, index=True)

    inspection_coordinator = fields.Char("Inspector")
    days = fields.Integer(string='Days')
    per_day_rate = fields.Float(string="Per Day Rate", store=True)
    add_expenses = fields.Float(string="AdditionalExp", store=True)
    amount = fields.Float(string="Amount", digits=(6, 2), compute="_amount_all", store=True)
    price_tax = fields.Float(string="Amount Tax", digits=(6, 2), compute="_amount_all", default=0.0, store=True)
    total = fields.Float(string="Total", digits=(6, 2), compute="_amount_all", store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes')
    summar_report_line_id = fields.Many2one('emp.list', copy=False, string="Report Line")
    calendar_ids = fields.Many2many('calendar.event', 'invoice_line_calendar_event_rel', 'invoice_line_id',
                                    'calendar_id',
                                    string='Calendar Events', copy=False, store=True)
    partner_ids = fields.Many2many('res.partner', 'invoice_line_res_partner_rel', 'invoice_line_id',
                                   'partner_id', string='Vendor', copy=False, store=True)

    @api.depends('days', 'per_day_rate', 'tax_id', 'add_expenses', 'stay')
    def _amount_all(self):
        for rec in self:
            rec.amount = rec.days * rec.per_day_rate
            rec.total = rec.amount + (rec.days * rec.stay) + rec.add_expenses
            if rec.tax_id:
                rec.price_tax = 0
                for tax in rec.tax_id:
                    rec.price_tax += rec.total * tax.amount / 100
            if not rec.tax_id:
                rec.price_tax = 0
