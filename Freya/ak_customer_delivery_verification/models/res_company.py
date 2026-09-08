# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    """
      Inherit and extend Odoo's ``res.company`` model to support configuration of
      delivery-related notification recipients.

      REF: user story 13

      This extension introduces the ``notification_share`` field, which allows
      companies to specify one or more email addresses (comma-separated) that
      should receive notifications related to the “Pay After Delivery” workflow
      or similar delivery-verification processes.
    """
    _inherit = 'res.company'

    notification_share = fields.Char(
        string='Pay After Delivery Notification Recipients',
        help='Comma-separated list of emails'
    )
