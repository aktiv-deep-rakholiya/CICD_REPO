# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportNumber(models.Model):
    _name = 'report.number'
    _description = "Report Number"

    name = fields.Char(string = 'Name', copy = False, default = 'New')
    visible = fields.Boolean(string = 'Display' , default = False, copy = False)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)

    @api.constrains('company_id', 'name')
    def _check_name_unique(self):
        for rec in self:
            if rec.name and rec.company_id:
                if rec.search([('company_id', '=', rec.company_id.id), ('name', '=', rec.name),
                                ('id', '!=', rec.id)]):
                    raise UserError(_("Report Number must be unique!"))
