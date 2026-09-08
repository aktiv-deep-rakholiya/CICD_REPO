# -*- coding: utf-8 -*-

from odoo import fields, models


class ClientInitiator(models.Model):
    _name = 'client.initiator'
    _description = "Client Initiator"

    name = fields.Char(string='Initiator Name')
