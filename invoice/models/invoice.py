from odoo import models ,fields ,api
from datetime import datetime
import calendar
from odoo.addons.base.models.res_currency import Currency


class Invoice(models.Model):
    _name = "invoice"
    _description = "prime Invoice"
    _rec_name = "invoice_no1"
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    summary_report_id = fields.Many2one('summary.report', string="Visit Summary", copy=False, tracking=True)
    invoice_no1 = fields.Char(string='Invoice No', translate=True, copy=False, index=True, default='Draft')
    project_id = fields.Many2one('project.project', tracking=True, string="Project", required=True)
    client_master_id = fields.Many2one('client.master', tracking=True, store=True, string='Client')

    @api.depends('client_master_id')
    def compute_client_name(self):
        for rec in self:
            if rec.client_master_id:
                rec.client_name = rec.client_master_id.client_name
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
    vat_code = fields.Char(string="Vat Code", tracking=True)
    tel_num = fields.Char(string="Tel Num", tracking=True)
    fax = fields.Char(string="Fax", tracking=True)
    attn = fields.Char(string="Attn", tracking=True)
    trn = fields.Char(string="TRN", tracking=True)
    street = fields.Char('Street', readonly=False)
    street2 = fields.Char('Street2', readonly=False)
    zip = fields.Char('Zip', change_default=True, readonly=False)
    city = fields.Char('City', readonly=False)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        readonly=False, store=True,
        domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        readonly=False, store=True)
    inv_date = fields.Date(string='Invoice Date', required=True, default=fields.Date.today())
    price_list = fields.Many2one(
        'pricelist.master', string='Pricelist', required=True)
    pay_term = fields.Many2one(
        'account.payment.term', string='Payment Terms',
        default=lambda self: self.env['account.payment.term'].search([('name', '=', '30 Days')], limit=1).id)

    purchase_id = fields.Many2one('purchase.order', string='Purchase Order No')
    currency = fields.Many2one('res.currency', string="Currency", required=True)
    amount_untaxed = fields.Float(string='Untaxed Amount', readonly=True, compute='_amount_all')
    amount_tax = fields.Float(string='Taxes', readonly=True, compute='_amount_all')
    amount_total = fields.Float(string='Total', readonly=True, tracking=4, compute='_amount_all')

    invoice_no = fields.One2many('invoice.note', 'inv_note')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    status = fields.Selection([
        ('draft', 'Drafted'),
        ('post', 'Posted'),
        ('cancel', 'Cancelled'),
    ], default='draft', copy=False)
    purchase_date = fields.Date(string='Purchase Date')
    due_date = fields.Date(string='Due Date')

    pay_status = fields.Selection([
        ('paid', 'Paid'),
        ('not_paid', 'Not Paid'),
    ], string='Payment Status', readonly=False, copy=False, index=True)
    client_id = fields.Many2one('client.details', string='Client Details',
                                default=lambda self: self.env['client.details'].search([], limit=1))
    is_tax_visible = fields.Boolean('Is tax visible???', default=False)

    aed_currency = fields.Float('AED Currency', compute="_compute_currency_aed", readonly=False, copy=False, store=True)

    @api.depends('currency')
    def _compute_currency_aed(self):
        for rec in self:
            params = self.env['ir.config_parameter'].sudo()
            eur_to_aed = float(params.get_param('invoice.eur_to_aed', default=0.0))
            usd_to_aed = float(params.get_param('invoice.usd_to_aed', default=0.0))
            if rec.currency.name == "EUR":
                rec.aed_currency = eur_to_aed
            elif rec.currency.name == "USD" or rec.currency.name == "AED":
                rec.aed_currency = usd_to_aed
            else:
                rec.aed_currency = 0.0

    @api.onchange('country_id')
    def onchange_inv_note(self):
        for rec in self:
            if rec.country_id.code == 'AE':
                rec.is_tax_visible = True
            else:
                rec.is_tax_visible = False
                rec.invoice_no.tax_id = False

    def update_client_details(self):
        for rec in self:
            rec.price_list = rec.client_master_id.price_list_id
            rec.pay_term = rec.client_master_id.payment_term_id
            rec.vat_code = rec.client_master_id.vat_code
            rec.attn = rec.client_master_id.attn
            rec.tel_num = rec.client_master_id.mobile
            rec.fax = rec.client_master_id.fax
            rec.trn = rec.client_master_id.trn
            rec.street = rec.client_master_id.street
            rec.street2 = rec.client_master_id.street2
            rec.fax = rec.client_master_id.fax
            rec.zip = rec.client_master_id.zip
            rec.city = rec.client_master_id.city
            rec.state_id = rec.client_master_id.state_id
            rec.country_id = rec.client_master_id.country_id
            rec.currency = rec.client_master_id.currency_id
            if rec.client_master_id.currency_id.name == "EUR":
                rec.aed_currency = float(
                    self.env['ir.config_parameter'].sudo().get_param('invoice.eur_to_aed'))
            elif rec.client_master_id.currency_id.name == "USD" or rec.currency.name == "AED":
                rec.aed_currency = float(
                    self.env['ir.config_parameter'].sudo().get_param('invoice.usd_to_aed'))
            rec.onchange_inv_note()
            rec._search_client()

    @api.onchange('client_master_id')
    def onchange_country_id(self):
        for rec in self:
            domain = []
            if rec.client_master_id:
                domain.append(('client_id', '=', rec.client_master_id.id))
                if rec.client_master_id.price_list_id:
                    rec.price_list = rec.client_master_id.price_list_id.id
                if rec.client_master_id.payment_term_id:
                    rec.pay_term = rec.client_master_id.payment_term_id.id
                if rec.client_master_id.street:
                    rec.street = rec.client_master_id.street
                if rec.client_master_id.street2:
                    rec.street2 = rec.client_master_id.street2
                if rec.client_master_id.city:
                    rec.city = rec.client_master_id.city
                if rec.client_master_id.state_id:
                    rec.state_id = rec.client_master_id.state_id.id
                if rec.client_master_id.country_id:
                    rec.country_id = rec.client_master_id.country_id.id
                if rec.client_master_id.currency_id:
                    rec.currency = rec.client_master_id.currency_id.id
                if rec.client_master_id.zip:
                    rec.zip = rec.client_master_id.zip
                return {'domain': {'price_list': domain}}
            else:
                return {}

    def _search_client(self):
        for rec in self:
            client_id = self.env['client.details'].search([('name', '=', rec.client_master_id.code)])
            if client_id:
                rec.client_id = client_id.id

    def confirm_statusbar(self):
        if self.status == 'draft':
            current_date_time = datetime.now()
            seq_code = 'invoice.no'
            if self.invoice_no1 == 'Draft':
                if self.client_master_id.sequence_code:
                    seq_code += "." + self.client_master_id.sequence_code
                else:
                    seq_code += '.seq'
                sequence = 'P4I' + '/' + str(self.env['ir.sequence'].next_by_code(seq_code)) + '/' + str(
                    self.client_master_id.sequence_code) + '/' + str(current_date_time.year)
                self.write({'invoice_no1': sequence or ('Draft')})
            self.write({'status': 'post'})

    def reset_statusbar(self):
        self.status = "draft"

    def cancel_statusbar(self):
        self.status = 'cancel'

    @api.depends('invoice_no', 'country_id', 'invoice_no.tax_id')
    def _amount_all(self):
        for order in self:
            amount_untaxed = total_tax = 0.0
            for line in order.invoice_no:
                amount_untaxed += line.total
                if line.price_tax:
                    total_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': round(total_tax),
                'amount_total': round(amount_untaxed + total_tax)
            })

    def aed_amount_to_textform(self, amount):
        currency = self.env['res.currency'].sudo().search([('name', '=', 'AED')])
        if currency:
            var_amt = Currency.amount_to_text(currency, float(amount))
        return var_amt[var_amt.rfind(' '):] + ' ' + var_amt[:-(len(var_amt) - var_amt.rfind(' '))]

    def amount_to_textform(self, amount, currency):
        if currency:
            var_amt = Currency.amount_to_text(currency, float(amount))
        else:
            var_amt = Currency.amount_to_text(self.env.company.currency_id.id, float(amount))
        return var_amt[var_amt.rfind(' '):] + ' ' + var_amt[:-(len(var_amt) - var_amt.rfind(' '))]

    def get_date_inv(self):
        return self.inv_date.strftime("%d-%b-%Y")

    def get_date(self, flag):
        if flag == 0:
            return datetime(self.inv_date.year, self.inv_date.month, 1).date().strftime("%d-%b-%Y")
        else:
            _, num_days = calendar.monthrange(self.inv_date.year, self.inv_date.month)

            return datetime(self.inv_date.year, self.inv_date.month, num_days).date().strftime("%d-%b-%Y")
