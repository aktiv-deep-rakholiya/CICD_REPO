# -*- coding: utf-8 -*-

from odoo import fields, models


class ProgressActivityLine(models.Model):

    _name = 'progress.activity.line'
    _description = "ProgressActivityLine"

    task_id = fields.Many2one('project.task',string='Task ID')
    planned_starting_date = fields.Date(string='Planned Starting')
    actual_starting_date = fields.Date(string='Actual Starting')
    expected_completion_date = fields.Date(string='Expected Completion Date')
    actual_completion_date = fields.Date(string='Actual Completion Date')
    subvendor_item = fields.Char(string='Item/Name')
    doc_po = fields.Char(string='Dwg/Doc Nr/PO Nr')
    delivery_date_order=fields.Date(string='Delivery Date By Order')
    delivery_date_promised=fields.Date(string='Delivery Date Promised')
    delivery_date_actual=fields.Date(string='Delivery Date Actual')
    sub_order_date_scheduled=fields.Date(string='Suborder Issue Date Scheduled')
    sub_order_date_actual=fields.Date(string='Suborder Issue Date Actual')
    subvendor_name=fields.Char(string='Sub Vendor Name')
    subvendor_po=fields.Char(string='Sub Vendor PONO')
    percentage=fields.Integer(string='Percent')
    name=fields.Many2one('activity.description',string='Activity Description')
