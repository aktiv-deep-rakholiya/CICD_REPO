# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_service_partner = fields.Boolean(string="Service Partner", copy=False, store=True)
