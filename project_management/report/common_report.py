from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.exceptions import UserError
import tempfile
import zipfile
import os
import base64


class CommonReport(models.AbstractModel):
    _name = 'common.report'
    _description = 'Common Report'

    filter_by = fields.Selection([
        ('period', 'Period Range'),
        ('month', 'Month'),
    ], default='month', string="Filter By")

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    month_data = fields.Char("Month")

    project_id = fields.Many2one('project.project', string="Project")
    vendor_id = fields.Many2one('res.partner', string="Vendor")
    inspector_id = fields.Many2one('inspector.name', string="Inspector")

    file = fields.Binary("File", readonly=True)
    file_name = fields.Char("File Name", readonly=True)

    @api.onchange('month_data')
    def onchange_month_data(self):
        value = self.month_data
        warning_message = False

        if value:
            # Format must be MM/YYYY
            if len(value) != 7 or value[2] != '/':
                warning_message = 'Month format should be MM/YYYY'

            else:
                mm, yyyy = value[:2], value[3:]

                if not (mm.isdigit() and 1 <= int(mm) <= 12):
                    warning_message = 'MM should be between 01 and 12'

                elif not yyyy.isdigit():
                    warning_message = 'Year must be numeric'

        if warning_message:
            self.month_data = False
            return {'warning': {'message': warning_message}}

    def _get_month_dates(self):
        if not self.month_data or len(self.month_data) != 7:
            raise UserError(_("Month format must be MM/YYYY"))

        month = self.month_data[:2]
        year = self.month_data[3:7]

        fromdate = datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d")
        enddate = fromdate + relativedelta.relativedelta(months=1) - timedelta(days=1)

        return fromdate.date(), enddate.date()

    def _get_calendar_domain(
            self,
            client_code,
            include_status=False,
            extra_domain=None,
    ):
        domain = []

        if self.project_id:
            domain.append(('project_id', 'in', self.project_id.ids))

        if client_code:
            domain.append(('code', '=',client_code ))

        if include_status:
            domain.append('|')
            domain.append(('include_timesheet', '=', True))
            domain.append(('status', '=', 'verified'))

        fromdate = todate = False
        if self.filter_by == 'month' and self.month_data:
            fromdate, todate = self._get_month_dates()
            domain.append(('start', '>=', str(fromdate)))
            domain.append(('start', '<=', str(todate)))

        if self.env.user.id != 2:
            domain.append(('inspection_coordinator', '=', self.env.user.id))

        if self.vendor_id:
            domain.append(('vendor_id', '=', self.vendor_id.id))

        if self.inspector_id:
            domain.append(('employee', '=', self.inspector_id.ins_name))

        if extra_domain:
            for dom in extra_domain:
                if dom:
                    domain.append(dom)

        return domain, fromdate, todate

    def _build_common_values(self, record):
        vendor = ''
        if record.vendor_id:
            vendor = ", ".join(v.name for v in record.vendor_id)
            if record.sub_vendor:
                vendor += "\nSubvendor: %s" % ", ".join(v.name for v in record.sub_vendor)

        return {
            'purchase': record.purchase_id.name if record.purchase_id else '',
            'vendor': vendor,
            'employee': record.employee or '',
            'employee_role': record.employee_role.name if record.employee_role else '',
            'category': record.employee_role.name if record.employee_role else '',
            'start': datetime.strptime(str(record.start), "%Y-%m-%d %H:%M:%S").strftime(
                "%d-%m-%Y") if record.start else '',
            'unique_no': record.unique_no.unique_no if record.unique_no else '',
            'number': record.rpt_number or '',
            'days': record.total_days or 0,
            'allday': record.allday,
            'halfday': record.half_day,
            'txn': record.txn,
        }

    def _group_calendar_records(self, calendar_event, value_builder):
        start_values_data = {}
        purchase_new = []
        for record in calendar_event:
            purchase = record.purchase_id.name if record.purchase_id else ''
            if purchase and purchase not in purchase_new:
                purchase_new.append(purchase)
            employee = record.employee or ''
            key = f"{record.vendor_id.name}_{employee}"

            category = record.employee_role.name if record.employee_role else ''
            values = value_builder(record)

            if key not in start_values_data:
                start_values_data[key] = {}

            if category not in start_values_data[key]:
                start_values_data[key][category] = []

            start_values_data[key][category].append(values)

        return start_values_data

    def _create_zip_from_xlsx_data(self, data):
        temp_dir = tempfile.mkdtemp()
        try:
            for filename, b64data in data:
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(base64.b64decode(b64data))

            zip_path = os.path.join(temp_dir, f"Timesheet-{self.project_id.name}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename in os.listdir(temp_dir):
                    if filename.endswith('.xlsx'):
                        zipf.write(os.path.join(temp_dir, filename), arcname=filename)

            with open(zip_path, 'rb') as zf:
                zip_content = base64.b64encode(zf.read())  # b64 bytes
                self.file = zip_content
                self.file_name = f"Timesheet-{self.project_id.name}.zip"

            # cleanup
            for filename in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, filename))
            os.rmdir(temp_dir)

        except Exception as e:
            raise UserError(_("Error while creating ZIP file. Please try again."))

    def generate_report_excel(self):
        pass
