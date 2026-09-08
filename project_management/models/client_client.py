# -*- coding: utf-8 -*-

from odoo import fields, models


class ClientOfClient(models.Model):
    _name = 'client.client'
    _description = "Client Of Client"

    name = fields.Char('Name', required=True)
