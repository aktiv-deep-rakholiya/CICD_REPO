# -*- coding: utf-8 -*-

from odoo import fields, models


class SubVendor(models.Model):
    _name = 'sub.vendor'
    _description = "SubVendor"

    name = fields.Char(string='Sub Vendor')
