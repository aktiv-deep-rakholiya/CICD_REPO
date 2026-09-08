# -*- coding: utf-8 -*-

from odoo import fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    hrs = fields.Integer(string='Hours')
    extra_hrs = fields.Integer(string='Extra Hrs')
    kms = fields.Integer(string='Kms')
    extra_kms = fields.Integer(string='Extra Kms')
    note = fields.Char(string ='Note')
    end_client = fields.Many2one('end.client'  ,string='End Client')
    abortive_visit = fields.Boolean(string='ABORTIVE VISIT', default=False)
    eigl_person_id = fields.Many2one('eigl.person', string='EIGL', tracking=True)
    project_id = fields.Many2one('project.project', string='Project', tracking=True)
    service_no = fields.Many2many(related='project_id.service_order_no_ids', string="Service Number")
    approver = fields.Many2one(related='project_id.approving_authority', string="Approver Name")
    purchase_id_multi = fields.Many2many('purchase.order', string="Purchase Order Multi ")
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order')
    job_assign = fields.Char(string ='Job Assignment')
    pscjob = fields.Char(string ='PSC Job')
    initiator_id = fields.Many2one('client.initiator', string='Initiator')
    txn = fields.Char(string ='TXN')
    notification_no = fields.Char(string='Notification No')
