# -*- coding: utf-8 -*-

from odoo import fields, models


class InspectorName(models.Model):
    _name = 'inspector.name'
    _description = "Inspector Name"
    _rec_name ='ins_name'

    ins_name = fields.Char(string='Inspector Name')
    per_day_rate = fields.Float(string = "Rate per Day", default = "0.0", copy = False)
    per_day_month = fields.Float(string="Rate per Month", default = "0.0", copy = False)
    employee_signature = fields.Binary(string='Inspector Signature')
