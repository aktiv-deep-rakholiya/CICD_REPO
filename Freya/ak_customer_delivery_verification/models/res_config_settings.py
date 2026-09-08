# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """
       Inherit and extend Odoo's ``res.config.settings`` model to expose the
       company-level delivery notification configuration in the system settings.

        REF: user story 13

       This extension adds a related field, ``notification_share``, which mirrors
       the corresponding field on ``res.company``. It allows administrators to
       configure the list of email recipients (for Pay After Delivery or delivery
       verification notifications) directly from the general settings interface.
    """
    _inherit = 'res.config.settings'

    notification_share = fields.Char(
        related='company_id.notification_share',
        store=True,
        readonly=False
    )
