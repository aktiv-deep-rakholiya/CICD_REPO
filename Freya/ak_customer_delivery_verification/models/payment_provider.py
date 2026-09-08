# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class PaymentProvider(models.Model):
    """
        Inherit and extend Odoo's ``payment.provider`` model to
        add support for delivery verification functionality.

        REF: user story 13

        This extension introduces a new configuration field,
        ``is_delivery_verification``, which allows each payment
        provider to enable or disable one-time delivery
        verification workflows. When activated, the provider can
        trigger additional validation steps—such as sending a
        verification email—during the payment or order confirmation process.
    """
    _inherit = "payment.provider"

    is_delivery_verification = fields.Boolean(
        string="Delivery Verification"
    )
