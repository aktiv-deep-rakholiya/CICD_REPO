# -*- coding: utf-8 -*-

from odoo import fields, models


class EnquirySequence(models.Model):
    _name = 'enquiry.sequence'
    _description = 'Enquiry Sequence'

    unique_no = fields.Many2one('project.enquiry', required=True, index=True)
    name = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=1)
