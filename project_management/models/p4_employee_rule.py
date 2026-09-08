# -*- coding: utf-8 -*-

from odoo import fields, models


class P4EmployeeRole(models.Model):
    _name = 'p4.employee.role'
    _description = "Prime Employee Rule"

    name = fields.Char(string='Employee Role')
