# -*- coding: utf-8 -*-

from odoo import fields, models


class EiglPerson(models.Model):
    _name = 'eigl.person'
    _description = "Eigl Person"

    name=fields.Char(string='EIGL')
