# -*- coding: utf-8 -*-

from odoo import fields, models


class TaskManagement(models.Model):
    _inherit='project.task'

    progress_activity_line=fields.One2many('progress.activity.line','task_id',string='Task Status')
