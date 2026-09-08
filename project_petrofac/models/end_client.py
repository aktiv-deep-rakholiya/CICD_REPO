# -*- coding: utf-8 -*-

from odoo import fields, models


class EndClient(models.Model):
    _name = 'end.client'
    _description = "End Client"

    name = fields.Char(string='End Client')
