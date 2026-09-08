# -*- coding: utf-8 -*-

from odoo import fields, models


class ActivityDescription(models.Model):
    _name = 'activity.description'
    _description = "Activity Description"

    activity_code = fields.Char(string='Activity Code')
    name = fields.Char(string='Activity Description')
