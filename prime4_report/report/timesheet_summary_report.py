from odoo import models, fields, api, _
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.exceptions import UserError
from collections import defaultdict


class TimesheetSummaryReport(models.TransientModel):
    _name = 'timesheet.summary.report'
    _inherit = 'common.report'
    _description = 'Summary of Timesheet Report'

    location_id = fields.Many2one('res.country', string="Location")

    def generate_report_excel(self):
        byte_io = BytesIO()
        workbook = xlsxwriter.Workbook(byte_io)
        worksheet = workbook.add_worksheet('Summary of Timesheet')
        # Set column widths
        worksheet.set_column('A:A', 18)
        worksheet.set_column('B:B', 18)
        worksheet.set_column('C:C', 39)
        worksheet.set_column('D:D', 42)
        worksheet.set_column('E:E', 19)
        worksheet.set_row(2, 25)
        # Define formats
        style_header = workbook.add_format(
            {'font_name': 'Arial','bold': True, 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#ccffff', 'border': 1, 'text_wrap': True})
        style_center_align = workbook.add_format({'font_name': 'Arial','font_size': 10,'align': 'center', 'valign': 'vcenter', 'border': 1, 'text_wrap': True})
        row = 0

        row += 2
        worksheet.write(row, 0, 'Project', style_header)
        worksheet.write(row, 1, 'Location', style_header)
        worksheet.write(row, 2, 'Name Of the Inspector / Expeditor', style_header)
        worksheet.write(row, 3, 'Vendor', style_header)
        worksheet.write(row, 4, 'Inspection Coordinator', style_header)

        if self.project_id:
            project = ('project_id', 'in', self.project_id.ids)
        else:
            all_project = self.env['project.project'].search([])
            project = ('project_id', 'in', all_project.ids)

        if self.vendor_id:
            vendor = ('vendor_id', '=', self.vendor_id.id)
        else:
            all_vendor = self.env['res.partner'].search([])
            vendor = ('vendor_id', 'in', all_vendor.ids)

        if self.location_id:
            location = ('v_location', '=', self.location_id.id)
        else:
            all_location = self.env['res.country'].search([])
            location = ('v_location', 'in', all_location.ids)

        if self.filter_by == 'period':
            if self.date_from and self.date_to:
                date_compare = ('start', '>=', self.date_from)
                date_compare1 = ('start', '<=', self.date_to)
                domain = [project, vendor, location, date_compare, date_compare1]
                from_format = self.date_from.strftime("%d/%m/%Y")
                to_format = self.date_to.strftime("%d/%m/%Y")

                worksheet.merge_range(0, 0, 1, 4, 'Summary of Time Sheet from ' + from_format + ' to ' + to_format,
                                   style_header)

        if self.filter_by == 'month':
            if self.month_data:
                month = self.month_data[0:2]
                year = self.month_data[3:7]
                from_date_join = str(year) + '-' + str(month) + '-01'
                fromdate = datetime.strptime(from_date_join, "%Y-%m-%d")
                enddate = fromdate + relativedelta.relativedelta(months=1) - timedelta(days=1)
                fromdate = fromdate.date()
                todate = enddate.date()
                enddate = enddate.date()
                date_compare = ('start', '>=', str(fromdate))
                date_compare1 = ('start', '<=', str(enddate))
                domain = [project, vendor, location, date_compare, date_compare1]
                if self.env.user.id != 2:
                    domain += [('inspection_coordinator', '=', self.env.user.id)]

                fromdate_month = fromdate.strftime("%b %Y")
                worksheet.merge_range(0, 0, 1, 4, 'Summary of Time Sheet for the month of ' + fromdate_month, style_header)

        calendar_event = self.env['calendar.event'].search(domain, order="project_id")

        if not calendar_event:
            raise UserError(_("No Record Found"))

        project_values = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

        for cal in calendar_event:
            project_values[cal.project_id][cal.v_location][cal.vendor_id][cal.employee] = (
                    str(cal.employee) + '-' + str(cal.employee_role.name))

        # Write the data to the Excel sheet
        for project in project_values:
            project_end_row = row
            for location in project_values[project]:
                location_end_row = row
                for vendor in project_values[project][location]:
                    vendor_end_row = row
                    vendor_row1 = row
                    for employee_role in project_values[project][location][vendor].values():
                        row += 1
                        employee_start_row = vendor_end_row + 1
                        vendor_row1 += 1
                        worksheet.write(row, 2, employee_role, style_center_align)
                    employee_end_row = vendor_row1
                    if employee_start_row != employee_end_row:
                        worksheet.merge_range(employee_start_row, 3, employee_end_row, 3, vendor.name,
                                              style_center_align)
                    else:
                        worksheet.write(employee_start_row, 3, vendor.name, style_center_align)
                    vendor_start_row = location_end_row + 1

                vendor_end_row1 = employee_end_row
                if vendor_start_row != vendor_end_row1:
                    worksheet.merge_range(vendor_start_row, 1, vendor_end_row1, 1, location.name, style_center_align)
                else:
                    worksheet.write(vendor_start_row, 1, location.name, style_center_align)
                project_start_row = project_end_row + 1

            project_end_row1 = vendor_end_row1
            if project_start_row != project_end_row1:
                worksheet.merge_range(project_start_row, 0, project_end_row1, 0, project.name, style_center_align)
            else:
                worksheet.write(project_start_row, 0, project.name, style_center_align)
            if project_start_row != project_end_row1:
                worksheet.merge_range(project_start_row, 4, project_end_row1, 4, self.env.user.name, style_center_align)
            else:
                worksheet.write(project_start_row, 4, self.env.user.name, style_center_align)


        # Save the file in memory
        workbook.close()
        file_data = byte_io.getvalue()
        file_content = base64.b64encode(file_data)

        # Write the file to the record
        self.write({
            'file': file_content,
            'file_name': 'summary_of_timesheet.xlsx'
        })

        level1_groups = self.env.ref('project_management.accounts_role')
        level1_users = self.env['res.users'].search([('groups_id', 'in', [level1_groups.id])])
        partner_ids = level1_users.mapped('partner_id')
        if partner_ids:
            attachments = self.env['ir.attachment'].sudo().create({
                'name': self.file_name,
                'type': 'binary',
                'datas': file_content,
                'res_model': 'timesheet.summary.report',
                'res_id': self.ids[0],
                'mimetype': 'application/vnd.ms-excel'
            })

            for partner_id in partner_ids:
                message = partner_id.message_post(
                    body='Report Has been Generated. Kindly Review it !',
                    message_type='notification',
                    attachment_ids=[attachments.id],
                    subtype_xmlid="mail.mt_comment",
                )
                self.env['mail.notification'].create({
                    'mail_message_id': message.id,
                    'res_partner_id': partner_id.id,
                    'notification_type': 'inbox',
                    'is_read': False,
                })

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(self.env.ref('prime4_report.timesheet_summary_report_view').id, 'form')],
            'res_model': 'timesheet.summary.report',
            'target': 'new',
            'context': self._context
        }
