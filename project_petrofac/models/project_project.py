# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectManagement(models.Model):
	_inherit = 'project.project'

	service_order_no_ids = fields.Many2many('service.number',string='Service Order Number')
	approving_authority = fields.Many2one('approver.person'  ,string='Approver Name')
