# -*- coding: utf-8 -*-

from odoo import fields, models


class LostWizard(models.TransientModel):
    _name = 'lost.wizard'
    _description = 'lost wizard'

    lost_reason = fields.Char(string='Lost Reason')

    def action_lost_reason(self):
        leads = self.env['project.enquiry'].browse(self.env.context.get('active_ids'))
        return leads.action_set_lost(self.lost_reason)
