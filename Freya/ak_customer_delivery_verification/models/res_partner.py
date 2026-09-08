# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    """
        Inherit and extend Odoo's ``res.partner`` model to support the
        "Pay After Invoice" functionality for contacts.

         REF: user story 13

        This extension introduces a new Boolean field, ``is_paid``, which can be
        used to indicate whether a partner is eligible for Pay After Invoice
        terms. The field is displayed in the Contact Form and can be referenced
        in payment, invoicing, or delivery workflows to control or track deferred
        payment behavior.
    """
    _inherit = 'res.partner'

    is_paid = fields.Boolean(
        string='Pay After Invoice',
        help='Boolean in Contact Form'
    )
