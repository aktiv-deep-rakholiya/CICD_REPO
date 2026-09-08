# -*- coding: utf-8 -*-

from odoo import fields, models


class AgencyNumber(models.Model):
    _name = 'agency.number'
    _description = "Agency Number"

    name = fields.Char(string='Agency Name')
