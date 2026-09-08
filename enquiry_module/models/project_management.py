# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProjectDescription(models.Model):
    _inherit = 'project.project'

    description = fields.Char("Project Description", index=True,tracking=True)
    proj_code = fields.Char(string="Project Code",index=True,required=True, tracking=True)
    client_id = fields.Many2one('client.master', copy=False, tracking = True)

    @api.depends('client_id')
    def compute_client_name(self):
        for rec in self:
            if rec.client_id:
                rec.client_name = rec.client_id.client_name
            else:
                rec.client_name = False

    client_name= fields.Selection([
        ('tcm', 'Tecnimont'),
        ('petrofac', 'Petrofac'),
        ('ace', 'ACE Plantech'),
        ('eneico', 'Eneico'),
        ('edif', 'Edif NDE'),
        ('equasrl', 'Equa SRL'),
        ('lindinger', 'Lindinger USA'),
        ('spxflow', 'Dollinger Filtration Limited'),
        ('global', 'Global SCS'),
        ('tecnicas','Tecnicas Reunidas'),
        ('tecton','Tecton'),
        ('arotec','Arotec'),
        ('clatech','Clatech Consulting Co.Ltd'),
        ('sisisrl','SISI SRL'),
        ('stamicarbon','STAMICARBON'),
        ('jkinspection','JK Inspection Engineering co ltd'),
        ('monarch','Monarch Style'),
        ('inspectorunion','Inspectors Union Co.'),
        ('swissapproval','Swiss Approval Team'),
        ('neilbarnett','Neil Barnett Inspection Services'),
        ('applus','Applus Velosi'),
        ('enzone','Enzone'),
        ('bureau','BUREAU Technical Services'),
        ('unitedglobal','United Global'),
        ('teleios','Teleios Spexxa Engg and Cons'),
        ('phbweser','PHB Weserhutte'),
        ('apollo', 'Apollo Electromechanical Contracting LLC'),
        ('eurture', 'Eurtrue'),
        ('others', 'Others'),
    ], string='Client', compute='compute_client_name')

    vat_code = fields.Char(string="Vat Code", index=True, tracking=True)
    tel_num = fields.Char(string="Tel Num", index=True, tracking=True)
    fax = fields.Char(string="Fax", index=True, tracking=True)
    attn = fields.Char(string="Attn", index=True, tracking=True)
    trn = fields.Char(string="TRN", index=True, tracking=True)

    # address
    street = fields.Char('Street', readonly=False)
    street2 = fields.Char('Street2', readonly=False)
    zip = fields.Char('Zip', change_default=True, readonly=False)
    city = fields.Char('City', readonly=False)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        readonly=False,
        domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        readonly=False)
    price_list = fields.Many2one(
        'product.pricelist', string='Pricelist')

    pay_term = fields.Many2one(
        'account.payment.term', string='Payment Terms')
    currency=fields.Many2one('res.currency',string="Currency")
    tax_id = fields.Many2many('account.tax', string='Taxes')
