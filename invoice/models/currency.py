from odoo import models ,fields ,api


class Currency(models.Model):
    _name = 'currency'
    _description = "Currency Conversion"
    _rec_name="currency_from"

    currency_from = fields.Selection([
        ("inr","INR"),
        ("aed","AED"),
        ("usd","USD"),
        ("gbp","GBP"),
        ],string="From Currency")

    currency_to = fields.Selection([
        ("euro","EURO"),
        ],string="To Currency",default='euro',readonly=True)
    
    rate=fields.Float(string="Conversion Rate",readonly=True,digits=(6,3),store=True)

    @api.onchange('currency_from')
    def onchange_currency_from(self):
            if self.currency_from == 'inr':
                self.rate = 0.015
            if self.currency_from == 'aed':
                self.rate = 0.25
            if self.currency_from == 'usd':
                self.rate = 0.95
            if self.currency_from == 'gbp':
                self.rate = 1.25
