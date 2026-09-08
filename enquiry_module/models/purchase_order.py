# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_date = fields.Date(string='Purchase Date')
    enquiry_id = fields.Many2one('project.enquiry', string ='Enquiry', copy = False, store = True)
