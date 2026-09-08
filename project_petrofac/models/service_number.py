# -*- coding: utf-8 -*-

from odoo import fields, models


class ServiceNumber(models.Model):
    _name = 'service.number'
    _description = "Service Number"

    name = fields.Char(string='Service Number')
