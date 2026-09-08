# -*- coding: utf-8 -*-

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _compute_tax_id(self):
        """Avoid taxes compute for service agreement"""
        sa_lines = self.filtered(lambda l: l.order_id.is_service_agreement)
        other_lines = self - sa_lines
        for line in sa_lines:
            line.taxes_id = self.env['account.tax'].browse()
        if other_lines:
            super(PurchaseOrderLine, other_lines)._compute_tax_id()

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, supplier, po):
        """Avoid taxes compute for service agreement"""
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, supplier, po
        )
        if po.is_service_agreement:
            res['taxes_id'] = [(6, 0, [])]
        return res

    @api.model_create_multi
    def create(self, vals_list):
        """Avoid taxes compute for service agreement"""
        lines = super().create(vals_list)
        sa_lines = lines.filtered(lambda l: l.order_id.is_service_agreement)
        if sa_lines:
            sa_lines._compute_tax_id()
        return lines

    def write(self, vals):
        """Avoid taxes compute for service agreement"""
        res = super().write(vals)
        if {'product_id', 'order_id'} & vals.keys():
            sa_lines = self.filtered(lambda l: l.order_id.is_service_agreement)
            if sa_lines:
                sa_lines._compute_tax_id()
        return res
