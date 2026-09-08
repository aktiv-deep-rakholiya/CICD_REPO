from odoo.addons.invoice.models.price_list import PriceList
from odoo import api, fields, models
from odoo.exceptions import UserError
import pandas as pd
import base64
from io import BytesIO


class UploadWizard(models.TransientModel):
    _name = 'upload.wizard'
    _description = "Upload Wizard"

    file = fields.Binary(string='Upload your File', attachment=True, store=True)

    file_name = fields.Char('File name')

    def action_upload_btn(self):
        file=self.file
        filename=BytesIO(base64.b64decode(file))
        xl_file = pd.read_excel(filename ,header=1,sheet_name='Sheet1')

        cat_location_dct = dict((y.strip().lower(), x) for x, y in
                                self.env['price.list'].fields_get(allfields=['cat_location'])['cat_location'][
                                    'selection'])
        services_dct = dict((y.strip().lower(), x) for x, y in
                                self.env['price.list'].fields_get(allfields=['services'])['services'][
                                    'selection'])

        for i in range(0,len(xl_file.index)):
            country = self.env['res.country'].search([('name', '=', xl_file.iat[i,1])], limit=1)
            employee_role = self.env['p4.employee.role'].search([('name', '=', xl_file.iat[i, 4])], limit=1)
            l=xl_file.iat[i, 2].strip().lower()
            v=  1  if xl_file.iat[i, 2].strip().lower() in services_dct.keys() else None
            vals={
                'pos': xl_file.iat[i,0],
                'country':country.id if country else None,
                'cat_location': cat_location_dct[xl_file.iat[i, 4].strip().lower()] if xl_file.iat[i, 4].strip().lower() in cat_location_dct.keys() else None,
                'services': services_dct[xl_file.iat[i, 2].strip().lower()] if xl_file.iat[i, 2].strip().lower() in services_dct.keys() else None,
                'employee_role': employee_role.id if employee_role else None,

                'oncall': xl_file.iat[i, 5],
                'resident1': xl_file.iat[i, 6],
                'resident2': xl_file.iat[i, 7],
                'resident3': xl_file.iat[i, 8],
                'resident4': xl_file.iat[i, 9],

                'oncall_without_night': xl_file.iat[i, 10],
                'oncall_with_night': xl_file.iat[i, 11],
                'oncall_without_night1': xl_file.iat[i, 12],
                'oncall_with_night1': xl_file.iat[i, 13],

                'resident_without_night_1': xl_file.iat[i, 14],
                'resident_with_night_1': xl_file.iat[i, 15],

                'resident_without_night_2': xl_file.iat[i, 16],
                'resident_with_night_2': xl_file.iat[i, 17],

                'resident_without_night_3': xl_file.iat[i, 18],
                'resident_with_night_3': xl_file.iat[i, 19],

                'resident_without_night_4': xl_file.iat[i, 20],
                'resident_with_night_4': xl_file.iat[i, 21],

                'remote_call': xl_file.iat[i, 22],
                'exp_remote': xl_file.iat[i, 23],
            }
            p=self.env['price.list'].create(vals)
