# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class ProductTemplateAttributeValue(models.Model):
    """
        Inherited: Product Template Attribute Value

        Extends the ``product.template.attribute.value`` model to introduce
        additional functionality or logic related to attribute values defined
        on product templates.
    """

    _inherit = "product.template.attribute.value"

    def _is_from_single_value_line(self, only_active=True):
        """
           Determine whether the record originates from an attribute line
           that has no other values associated with it.

           Parameters
           ----------
           only_active : bool, optional
               If True (default), only active attribute values are considered.
               If False, both active and archived values are included.

           Returns
           -------
           bool
               True if the attribute line has zero applicable values (active-only
               or all, depending on `only_active`); False otherwise.
        """
        self.ensure_one()
        all_values = self.attribute_line_id.product_template_value_ids
        if only_active:
            all_values = all_values._only_active()
        return len(all_values) == 0
