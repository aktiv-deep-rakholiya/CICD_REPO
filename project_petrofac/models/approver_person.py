# -*- coding: utf-8 -*-

from odoo import fields, models


class ApproverPerson(models.Model):
    _name = "approver.person"
    _description = "Approver Person"

    name = fields.Char(string='Approver Name')
