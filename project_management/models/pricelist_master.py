# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PriceListMaster(models.Model):
    _name = 'pricelist.master'
    _description = "PriceList Master"
    _order = "id desc"

    name = fields.Char(string = 'Name', copy = False, default = 'New')
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    client_id = fields.Many2one('client.master',  required=True)

    @api.constrains('company_id', 'name')
    def _check_name_unique(self):
        for rec in self:
            if rec.name and rec.company_id:
                if rec.search([('company_id', '=', rec.company_id.id), ('name', '=', rec.name),
                                ('id', '!=', rec.id)]):
                    raise UserError(_("Name must be unique!"))
