# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.phone_validation.tools import phone_validation
from odoo.exceptions import UserError


class ClientMaster(models.Model):
    _name = 'client.master'
    _description = "Client Master"

    name = fields.Char(string = 'Name', copy = False, default = 'New')
    code = fields.Char(string='Report Code', copy=False ,store = True)
    sequence_code = fields.Char(string = 'Code', copy= False, store = True)
    price_list_id = fields.Many2one('pricelist.master', string = 'PriceList', copy = False,store = True)
    payment_term_id = fields.Many2one('account.payment.term', string = 'Payment Term',  copy = False,store = True)
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
    ], string='Client')
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    vat_code = fields.Char(string="Vat", index=True)
    attn = fields.Char(string="Attn", index=True)
    mobile = fields.Char(string="Mobile", index=True)
    fax = fields.Char(string="Fax", index=True)
    trn = fields.Char(string="TRN", index=True)
    street = fields.Char('Street', readonly=False)
    street2 = fields.Char('Street2', readonly=False)
    email = fields.Char('Email', readonly=False)
    zip = fields.Char('Zip', change_default=True, readonly=False)
    city = fields.Char('City', readonly=False)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        readonly=False,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        readonly=False, store=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True)
    tax_ids = fields.Many2many('account.tax', string="Tax")

    @api.onchange('mobile', 'country_id', 'company_id')
    def _onchange_mobile_validation(self):
        if self.mobile:
            self.mobile = self._phone_format(self.mobile)

    def _phone_format(self, number, country=None, company=None):
        country = country or self.country_id or self.env.company.country_id
        if not country:
            return number
        return phone_validation.phone_format(
            number,
            country.code if country else None,
            country.phone_code if country else None,
            force_format='INTERNATIONAL',
            raise_exception=False
        )

    @api.constrains('code', 'company_id', 'name')
    def _check_name_unique(self):
        for rec in self:
            if rec.code and rec.company_id:
                if rec.search([('company_id', '=', rec.company_id.id), ('code', '=', rec.code),
                                ('id', '!=', rec.id)]):
                    raise UserError(_("Code must be unique!"))
            if rec.name and rec.company_id:
                if rec.search([('company_id', '=', rec.company_id.id), ('name', '=', rec.name),
                                ('id', '!=', rec.id)]):
                    raise UserError(_("Name must be unique!"))
