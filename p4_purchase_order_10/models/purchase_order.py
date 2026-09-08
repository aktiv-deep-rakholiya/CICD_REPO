# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_service_agreement = fields.Boolean('Service Agreement',copy=False)
    mail_dated = fields.Date("Agreed email Dated")
    attn = fields.Char("Attn")
    po_ref = fields.Char("PO Ref")
    client_rate = fields.Text("Client Rate")
    rpt_lind = fields.Boolean("Lindinger")
    rpt_petro = fields.Boolean("Petroleum")
    rpt_prime = fields.Boolean("Prime")
    rate_type = fields.Selection([
        ('man_day', 'Man Day'),
        ('man_month', 'Man Month')
    ], 'Rate Type', default='man_day')
    deliverable = fields.Selection([
        ('visitreport', 'Visit Report'),
        ('flashreport', 'Flash Report'),
        ('inspectionreport', 'Inspection Report'),
        ('expeditingreport', 'Expediting Report'),
        ('expeditinginspect', 'Inspection & Expediting Report'),
        ('auditreport', 'Audit Report'),
        ('loadingreport', 'Loading Report'),
        ('unloadingreport', 'Unloading Report'),
        ('loading/unloadingreport', 'Loading/Unloading Report'),
        ('otherreport', 'Other Report')
    ], 'Deliverable', default='inspectionreport')
    client_id = fields.Many2one('client.master', tracking=True, store=True)
    project_id = fields.Many2one('project.project', tracking=True, store=True)
    description = fields.Text(string='Description', tracking=True, store=True)
    partner_id = fields.Many2one(
        'res.partner',
        domain="[('is_service_partner', '=', is_service_agreement)]",
    )
