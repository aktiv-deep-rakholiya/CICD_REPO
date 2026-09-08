# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime


class SummaryReport(models.Model):
    _name = 'summary.report'
    _description = "Summary Report"
    _rec_name = 'project_id'
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date_from = fields.Date('Date From', default=False, copy=False)
    date_to = fields.Date('Date To', default=False, copy=False)
    name = fields.Char(string='Name', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    month_data = fields.Char(string="Month Data")
    project_id = fields.Many2one('project.project', string="Project")
    approve = fields.Boolean(string='Approve', default=False, readonly=True)
    not_approve = fields.Boolean(string='Not Approve', default=False, readonly=True)
    remark = fields.Char(string="Remark")
    inspection_coordinator = fields.Many2many('inspector.name', 'summary_report_inspector_id_rel', 'summary_id',
                                              'inspector_id', "Inspection Coordinator",
                                              tracking=True)
    date = fields.Date('Date', default=False)
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order No')
    client_id = fields.Many2many('client.master', 'client_summary_report', 'client_id', 'summary_id', tracking=True)
    invoice_ids = fields.One2many('invoice', 'summary_report_id', string='Invoices')
    invoice_count = fields.Integer(string='Invoice Orders', compute='_compute_invoice_ids')
    invoiced = fields.Boolean(string='Invoiced', default=False, store=True, compute='_compute_invoiced')

    @api.depends('invoice_ids.status')
    def _compute_invoiced(self):
        for rec in self:
            rec.invoiced = False
            if any(inv.status == 'post' for inv in rec.invoice_ids):
                rec.invoiced = True

    def action_view_invoices(self):
        action = self.env["ir.actions.actions"]._for_xml_id("invoice.gen_action_price_list")

        if len(self.invoice_ids) > 1:
            action['domain'] = [('id', 'in', self.invoice_ids.ids)]
        elif self.invoice_ids:
            form_view = [(self.env.ref('invoice.invoice_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = self.invoice_ids.id
        return action

    @api.depends('invoice_ids')
    def _compute_invoice_ids(self):
        for order in self:
            order.invoice_count = len(order.invoice_ids)

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

    ], string='Client', tracking=True, compute='compute_client_name')

    street = fields.Char('Street', readonly=False)
    street2 = fields.Char('Street2', readonly=False)
    zip = fields.Char('Zip', change_default=True, readonly=False)
    city = fields.Char('City', readonly=False)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        readonly=False)
    price_list = fields.Many2one(
        'pricelist.master', string='Pricelist', required=False)

    pay_term = fields.Many2one(
        'account.payment.term', string='Payment Terms',
        default=lambda self: self.env['account.payment.term'].search([('name', '=', '30 Days')], limit=1).id)

    currency = fields.Many2one('res.currency', string="Currency")

    vat_code = fields.Char(string="Vat Code", index=True, tracking=True)
    tel_num = fields.Char(string="Tel Num", index=True, tracking=True)
    fax = fields.Char(string="Fax", index=True, tracking=True)
    attn = fields.Char(string="Attn", index=True, tracking=True)
    trn = fields.Char(string="TRN", index=True, tracking=True)
    purchase_date = fields.Date(string='Purchase Date')

    emp_list = fields.One2many('emp.list', 'emp_id')

    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            if rec.project_id:
                rec.client_name = rec.project_id.client_name

    def action_approve(self):
        for record in self:
            if self.env.user.has_group('project_management.group_p4_coordinator') and not self.env.user.has_group(
                    'base.group_system'):
                raise UserError(_("Action Cannot be performed !!"))
            record.write({
                'approve': True,
                'not_approve': False,
                'remark': "",
                'inspection_coordinator': None,
            })

    def action_unapprove(self):

        for record in self:
            if not record.remark:
                raise UserError(_("Remark is Mandatory"))
            if not record.inspection_coordinator:
                raise UserError(_("Inspection Coordinator Name is Mandatory"))

            record.write({
                'not_approve': True,
                'approve': False
            })

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('visit.summary') or _('New')
        result = super(SummaryReport, self).create(vals_list)
        return result

    def invoice_btn(self):
        if False in [item.approve for item in self]:
            raise UserError(_("Please make sure the Records are Approved"))

        count = 0
        today = datetime.now()
        summary_report = self.env['summary.report'].search([('id', '=', self.id)])
        client_ids = set(summary_report.mapped('emp_list').mapped('client_id'))

        for client in client_ids:
            summary_line = self.env['emp.list'].search([('emp_id', '=', self.id), ('client_id', '=', client.id)])

            grouped_lines = {}

            for line in summary_line:
                aed_currency = 0.0
                pay_term = line.client_id.payment_term_id.id if line.client_id.payment_term_id else line.emp_id.pay_term.id
                price_list = line.client_id.price_list_id.id if line.client_id.price_list_id else line.emp_id.price_list.id
                street = line.client_id.street if line.client_id.street else line.emp_id.street
                street2 = line.client_id.street2 if line.client_id.street2 else line.emp_id.street2
                city = line.client_id.city if line.client_id.city else line.emp_id.city
                state_id = line.client_id.state_id.id if line.client_id.state_id else line.emp_id.state_id.id
                country_id = line.client_id.country_id.id if line.client_id.country_id else line.emp_id.country_id.id
                currency = line.client_id.currency_id.id if line.client_id.currency_id else line.emp_id.currency.id
                currency_name = self.env['res.currency'].sudo().search([('id','=',currency)]).name
                zip = line.client_id.zip if line.client_id.zip else line.emp_id.zip
                taxes = line.client_id.tax_ids if line.client_id.tax_ids else line.emp_id.emp_list.tax_id
                if currency_name == "EUR":
                    aed_currency = float(self.env['ir.config_parameter'].sudo().get_param('invoice.eur_to_aed'))
                elif currency_name == "USD" or currency_name == "AED":
                    aed_currency = float(self.env['ir.config_parameter'].sudo().get_param('invoice.usd_to_aed'))
                count += 1

                inv_vals = {
                    "summary_report_id": line.emp_id.id,
                    "project_id": line.emp_id.project_id.id,
                    "client_name": line.client_id.name,
                    "street": street,
                    "street2": street2,
                    "zip": zip,
                    "city": city,
                    "state_id": state_id,
                    "country_id": country_id,
                    "price_list": price_list,
                    "pay_term": pay_term,
                    "currency": currency,
                    "aed_currency": aed_currency,
                    "vat_code": line.client_id.vat_code,
                    "tel_num": line.client_id.mobile,
                    "fax": line.client_id.fax,
                    "attn": line.client_id.attn,
                    "trn": line.client_id.trn,
                    "purchase_date": line.emp_id.purchase_date,
                    "inv_date": today,
                    "client_master_id": line.client_id.id,
                }

                price_list = self.env['price.list'].search(
                    [
                        ('country', '=', line.country.id),
                        ('services', '=', line.services),
                        ('employee_role', '=', line.employee_role.id),
                        ('cat_location', '=', line.cat_location)
                    ]
                )

                if price_list.exists:
                    stay = 0
                    if line.with_stay:
                        stay = price_list.oncall_with_night
                    elif line.without_stay:
                        stay = price_list.oncall_without_night

                    if line.category_expenses == 'oncall':
                        try:
                            amt = float(price_list.oncall)
                        except:
                            amt = None
                    elif line.category_expenses == "resident1":
                        try:
                            amt = float(price_list.resident1)
                        except:
                            amt = None
                    elif line.category_expenses == "resident2":
                        try:
                            amt = float(price_list.resident2)
                        except:
                            amt = None
                    elif line.category_expenses == "resident3":
                        try:
                            amt = float(price_list.resident3)
                        except:
                            amt = None
                    elif line.category_expenses == "resident4":
                        try:
                            amt = price_list.resident4
                        except:
                            amt = None
                    else:
                        amt = 100

                group_key = (
                    line.country.id,
                    line.employee_role.id,
                    line.cat_location,
                    line.category_expenses,
                    line.client_name,
                    line.services,
                    line.emp_name,
                    tuple(line.partner_ids.ids)
                )

                if group_key not in grouped_lines:
                    grouped_lines[group_key] = {
                        "summar_report_line_id": [],
                        "country": line.country.id,
                        "employee_role": line.employee_role.id,
                        "cat_location": line.cat_location,
                        "category_expenses": line.category_expenses,
                        "client_name1": line.client_name,
                        "services": line.services,
                        "inspection_coordinator": line.emp_name,
                        "days": 0,
                        "add_expenses": 0,
                        "per_day_rate": amt,
                        "stay": stay,
                        "calendar_ids": [],
                        "partner_ids": line.partner_ids.ids,
                        "purchase_id": line.purchase_id.id,
                        "tax_id": line.client_id.tax_ids.ids,
                    }

                grouped_lines[group_key]["summar_report_line_id"].append(line.id)
                grouped_lines[group_key]["days"] += line.days
                grouped_lines[group_key]["add_expenses"] += line.add_expenses
                grouped_lines[group_key]["calendar_ids"].extend(line.calendar_ids.ids)

            for group_key, grouped_vals in grouped_lines.items():
                client_id = summary_line.filtered(lambda l: l.id == grouped_vals["summar_report_line_id"][0]).client_id.id
                invoice_available = self.env['invoice'].search(
                    [('client_master_id', '=', client_id), ('summary_report_id', '=', self.id)]
                )
                invoice_line_available = self.env['invoice.note'].search(
                    [('inv_note', '=', invoice_available.id), ('summar_report_line_id', 'in', grouped_vals["summar_report_line_id"])]
                )

                if invoice_available and not invoice_line_available:
                    invoice_available.write({'invoice_no': [(0, 0, {
                        # Here you should handle each field properly
                        "summar_report_line_id": grouped_vals["summar_report_line_id"][0],
                        "country": grouped_vals["country"],
                        "employee_role": grouped_vals["employee_role"],
                        "cat_location": grouped_vals["cat_location"],
                        "category_expenses": grouped_vals["category_expenses"],
                        "client_name1": grouped_vals["client_name1"],
                        "services": grouped_vals["services"],
                        "inspection_coordinator": grouped_vals["inspection_coordinator"],
                        "days": grouped_vals["days"],
                        "add_expenses": grouped_vals["add_expenses"],
                        "per_day_rate": grouped_vals["per_day_rate"],
                        "stay": grouped_vals["stay"],
                        "calendar_ids": [(6, 0, grouped_vals["calendar_ids"])],
                        "partner_ids": [(6, 0, grouped_vals["partner_ids"])],
                        "purchase_id": grouped_vals["purchase_id"],
                        "tax_id": [(6, 0, grouped_vals["tax_id"])]
                    })]})
                elif not invoice_available:
                    # Create invoice with inv_vals only
                    invoice = self.env['invoice'].create(inv_vals)
                    # Update invoice with grouped line values
                    invoice.write({'invoice_no': [(0, 0, {
                        "summar_report_line_id": grouped_vals["summar_report_line_id"][0],
                        "country": grouped_vals["country"],
                        "employee_role": grouped_vals["employee_role"],
                        "cat_location": grouped_vals["cat_location"],
                        "category_expenses": grouped_vals["category_expenses"],
                        "client_name1": grouped_vals["client_name1"],
                        "services": grouped_vals["services"],
                        "inspection_coordinator": grouped_vals["inspection_coordinator"],
                        "days": grouped_vals["days"],
                        "add_expenses": grouped_vals["add_expenses"],
                        "per_day_rate": grouped_vals["per_day_rate"],
                        "stay": grouped_vals["stay"],
                        "calendar_ids": [(6, 0, grouped_vals["calendar_ids"])],
                        "partner_ids": [(6, 0, grouped_vals["partner_ids"])],
                        "purchase_id": grouped_vals["purchase_id"],
                        "tax_id": [(6, 0, grouped_vals["tax_id"])]
                    })]})
