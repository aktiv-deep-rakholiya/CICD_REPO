from  odoo import models ,fields ,api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    eur_to_aed = fields.Float(string="EUR To AED Currency")
    usd_to_aed = fields.Float(string="USD To AED Currency")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            eur_to_aed=float(params.get_param('invoice.eur_to_aed', default=0.0)),
            usd_to_aed=float(params.get_param('invoice.usd_to_aed', default=0.0)),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('invoice.eur_to_aed', self.eur_to_aed or 0.0)
        params.set_param('invoice.usd_to_aed', self.usd_to_aed or 0.0)
        rec = self.env['invoice'].sudo().search([])
        for rec in rec:
            if rec.currency.name == "EUR":
                rec.write({
                    'aed_currency': self.eur_to_aed
                })
            elif rec.currency.name == "USD" or rec.currency.name == "AED":
                rec.write({
                    'aed_currency': self.usd_to_aed
                })
            else:
                rec.write({
                    'aed_currency': 0.0
                })
