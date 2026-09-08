# -*- coding: utf-8 -*-


from odoo import fields, models


class project_management(models.Model):
    _inherit = 'project.project'

    project_id = fields.Char(string='Project ID')
    planned_start_date = fields.Date(string='Planned Start Date')
    planned_end_date = fields.Date(string='Planned End Date')
    actual_start_date = fields.Date(string='Actual Start Date')
    actual_end_date = fields.Date(string='Actual End Date')
    material_description = fields.Text(string='Material Description')
    doc_number = fields.Char(string='Document Number')
    tcm_job = fields.Char(string='TCM Job Number')
    material_requisition_no = fields.Char(string='Material Requisition Number')
    expediting_date = fields.Date(string='Expediting Date')
    next_expediting_date = fields.Date(string='Next Expediting Date')
    vendor_id = fields.Many2one(related='purchase_id.partner_id',store = True,string='Vendor',domain="[('supplier','=',True),('is_company','=',True)]")
    purchase_id = fields.Many2one('purchase.order',string='Purchase Order')
    expediting_contract_no = fields.Char('Expediting Contract')
    inspection_contract_no = fields.Char('Inspection Contract')
