# -*- coding: utf-8 -*-

from odoo import fields, models


class Employee(models.Model):
	_inherit = 'hr.employee'

	employee_signature = fields.Binary(string='Employee Signature')
