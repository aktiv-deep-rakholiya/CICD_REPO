from odoo import models ,fields


class ClientDetails(models.Model):
    _name = 'client.details'
    _description = "Client Details"

    name = fields.Char(string="Client Name")
    stamp_image = fields.Binary(string="Stamp Image")
    sign_image = fields.Binary(string="Sign Image")
