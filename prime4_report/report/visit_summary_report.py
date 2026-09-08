from odoo import models, fields, api, _
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.exceptions import UserError
from odoo.tools.misc import file_path as get_file_path
from odoo.addons.project_management import report_common_method


class VisitSummaryReport(models.TransientModel):
    _name = 'visit.summary.report'
    _inherit = 'common.report'
    _description = 'Timesheet Report'

    role_id = fields.Many2one('p4.employee.role', string="Role")

    def generate_report_excel(self):
        byte_io = BytesIO()
        workbook = xlsxwriter.Workbook(byte_io)
        worksheet = workbook.add_worksheet('Timesheet Report')

        # Define formats
        style_header = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1, 'font_size': 8})
        style_header2 = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1,
             'bg_color': '#ffffcc', 'font_size': 8})
        style_header_new = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1, 'font_size': 8})
        style_header_new_left = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'border': 1, 'font_size': 8})
        style_header_new_right = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True, 'border': 1, 'font_size': 8})
        style_center_align = workbook.add_format(
            {'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 8, 'text_wrap': True})
        style_center_align_wrap = workbook.add_format(
            {'font_name': 'Arial', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 8, 'text_wrap': True})
        # Set column widths
        worksheet.set_column('A:A', 9)
        worksheet.set_column('B:B', 23)
        worksheet.set_column('C:C', 13)
        worksheet.set_column('D:D', 6)
        worksheet.set_column('E:E', 7)
        worksheet.set_column('F:F', 16)
        worksheet.set_column('G:G', 13)
        worksheet.set_column('H:H', 3)
        worksheet.set_column('I:I', 3)
        worksheet.set_column('J:J', 7)
        worksheet.set_column('K:K', 8)

        image_path = get_file_path('prime4_report/static/src/img/logo.jpg')
        with open(image_path, 'rb') as f:
            img_bytes = BytesIO(f.read())

        img_bytes.seek(0)
        worksheet.set_row(0, 15)
        worksheet.insert_image(0, 0,'logo.jpg', {
            'image_data': img_bytes,
            'x_scale': 0.4,
            'y_scale': 0.4,
            'x_offset': 4,
            'y_offset': 3,
        })

        # Writing some metadata
        worksheet.write(3, 4, 'Contract', style_header)
        if self.role_id.name == 'Inspector':
            if self.project_id.inspection_contract_no:
                worksheet.write(3, 5, self.project_id.inspection_contract_no, style_header2)
            else:
                worksheet.write(3, 5, '', style_header2)
        elif self.role_id.name == 'Expeditor':
            if self.project_id.expediting_contract_no:
                worksheet.write(3, 5, self.project_id.expediting_contract_no, style_header2)
            else:
                worksheet.write(3, 5, '', style_header2)
        elif self.role_id.name == 'Specialist Inspector':
            if self.project_id.expediting_contract_no:
                worksheet.write(3, 5, self.project_id.inspection_contract_no, style_header2)
            else:
                worksheet.write(3, 5, '', style_header2)

        else:
            worksheet.write(3, 5, '', style_header2)
        worksheet.merge_range(3, 7, 3, 8, 'Month', style_header_new_left)

        # Additional info (like agency, country, etc.)
        worksheet.write(4, 0, 'Agency', style_header_new)
        company = self.env['res.company'].search([])[0]
        worksheet.write(4, 1, company.name, style_header2)
        worksheet.merge_range(4, 7, 4, 8, 'Country', style_header_new_left)

        # Add table headers
        worksheet.write(6, 0, 'P.O. Nr.', style_header)
        worksheet.write(6, 1, 'VENDOR', style_header)
        worksheet.write(6, 2, 'INSPECTOR', style_header)
        worksheet.write(6, 3, 'ROLE', style_header)
        worksheet.write(6, 4, 'VISIT DATE', style_header)
        worksheet.write(6, 5, 'REPORT NUMBER', style_header)
        worksheet.write(6, 6, 'EIGL (or PEIL)', style_header)
        worksheet.merge_range(6, 7, 6, 8, '', style_header2)
        worksheet.write(6, 9, 'Expenses \nEUR', style_header)
        worksheet.write(6, 10, 'Expenses \nDescription', style_header)

        worksheet.write(7, 0, '', style_header)
        worksheet.write(7, 1, '', style_header)
        worksheet.write(7, 2, '', style_header)
        worksheet.write(7, 3, '', style_header)
        worksheet.write(7, 4, '', style_header)
        worksheet.write(7, 5, '', style_header)
        worksheet.write(7, 6, '', style_header)
        worksheet.write(7, 7, 'OD', style_header2)
        worksheet.write(7, 8, 'HD', style_header2)
        worksheet.write(7, 9, '', style_header)
        worksheet.write(7, 10, '', style_header)

        if self.project_id:
            project = ('project_id', '=', self.project_id.id)
        else:
            all_project = self.env['project.project'].search([])
            project = ('project_id', 'in', all_project.ids)

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
                user = ('inspection_coordinator', '=', self.env.user.id)
                domain = [user, project,date_compare, date_compare1]

                if self.vendor_id:
                    domain += [('vendor_id', '=', self.vendor_id.id)]
                if self.role_id:
                    domain += [('employee_role', '=', self.role_id.id)]
                if self.inspector_id:
                    domain += [('employee', '=', self.inspector_id.ins_name)]


        calendar_event = self.env['calendar.event'].search(domain, order="start")
        if not calendar_event:
            raise UserError(_("No Record Found"))

        start_values_data = {}
        purchase_new = []
        row = 7
        # Loop through the calendar events
        for record in calendar_event:
            start_values = {
                'purchase': record.purchase_id.name if record.purchase_id else '',
                'vendor': '',
                'employee': record.employee or '',
                'employee_role': record.employee_role.name or '',
                'start': datetime.strptime(str(record.start), "%Y-%m-%d %H:%M:%S").strftime(
                    "%d/%m/%Y") if record.start else '',
                'number': record.rpt_number or '',
                'eigl_person': record.eigl_person_id.name if record.eigl_person_id else '',
                'allday': False if record.half_day else True,  # If half_day is True, then it's not allday
                'halfday': True if record.half_day else False
            }

            # Process vendor details
            if record.vendor_id:
                vendor = ", ".join([job.name for job in record.vendor_id])
                if record.sub_vendor:
                    vendor_sub = ", ".join([job.name for job in record.sub_vendor])
                    vendor = f"Vendor: {vendor}\nSubvendor: {vendor_sub}"
            start_values['vendor'] = vendor or ''

            # Handle start values in dictionary for sorting later
            start = datetime.strptime(start_values['start'], "%d/%m/%Y") if start_values['start'] else None
            if start:
                if start not in start_values_data:
                    start_values_data[start] = []
                start_values_data[start].append(start_values)

            # Track purchases for summary later
            if start_values['purchase']:
                purchase_new.append(start_values['purchase'])

        totol_fullday = 0
        totol_halfday = 0
        # Render Excel rows based on sorted data
        for start_date, records in sorted(start_values_data.items()):
            if any(val['halfday'] for val in records):
                totol_halfday += 1
            else:
                totol_fullday += 1
            end_row = row
            row1 = row
            halfday_check = 0
            multiple_records = len(records) > 1

            # Count total full day and half day
            for val in records:
                row += 1
                start_row = end_row + 1
                row1 += 1

                # Write to Excel sheet for the current row
                worksheet.write(row, 0, val['purchase'], style_center_align_wrap)
                worksheet.write(row, 1, val['vendor'], style_center_align_wrap)
                worksheet.write(row, 2, val['employee'], style_center_align)
                worksheet.write(row, 3, val['employee_role'], style_center_align)
                worksheet.write(row, 5, val['number'], style_center_align)
                worksheet.write(row, 6, val['eigl_person'], style_center_align)

                # Handle halfday/allday rendering in Excel
                if val['halfday']:
                    halfday_check = 1

                worksheet.write(row, 7, '-', style_center_align)
                worksheet.write(row, 8, '-', style_center_align)
                worksheet.write(row, 9, '-', style_center_align)
                worksheet.write(row, 10, '-', style_center_align)

            end_row = row1

            start_val = records[0]['start']
            if multiple_records:
                worksheet.merge_range(start_row, 4, end_row, 4, start_val, style_center_align)
                # Merge cells based on halfday or allday status
                if halfday_check == 1:
                    worksheet.merge_range(start_row, 8, end_row, 8, 1.0, style_center_align)
                else:
                    worksheet.merge_range(start_row, 7, end_row, 7, 1.0, style_center_align)
            else:
                worksheet.write(start_row, 4, start_val, style_center_align)
                if halfday_check == 1:
                    worksheet.write(start_row, 8, 1.0, style_center_align)
                else:
                    worksheet.write(start_row, 7, 1.0, style_center_align)

        # Write summary (totals)
        next_row = end_row + 1
        worksheet.write(next_row, 0, '', style_header)
        worksheet.write(next_row, 1, '', style_header)
        worksheet.write(next_row, 2, '', style_header)
        worksheet.write(next_row, 3, '', style_header)
        worksheet.write(next_row, 4, '', style_header)
        worksheet.write(next_row, 5, '', style_header)
        worksheet.write(next_row, 6, '', style_header)
        worksheet.write(next_row, 7, str(totol_fullday), style_center_align)
        worksheet.write(next_row, 8, str(totol_halfday), style_center_align)
        worksheet.write(next_row, 9, '', style_header)
        worksheet.write(next_row, 10, '', style_header)

        # Write calendar start date
        if calendar_event and calendar_event[0].start:
            calendar_start_date = calendar_event[0].start.strftime("%b-%Y")
            worksheet.write(3, 6, calendar_start_date, style_header_new_right)
        else:
            worksheet.write(3, 6, '', style_header_new_right)

        # Write project and purchase information
        string = "\n".join(
            [purchase if i % 2 == 0 else ", " + purchase for i, purchase in enumerate(set(purchase_new))])
        data_project = f"{self.project_id.name}; PO# {string}"
        worksheet.write(4, 4, 'Project', style_header_new)
        worksheet.write(4, 5, data_project, style_header_new)
        worksheet.write(4, 6, calendar_event[0].v_location.name, style_header_new_right)

        workbook.close()
        file_data = byte_io.getvalue()
        file_content = base64.b64encode(file_data)

        # Write the file to the record
        self.write({
            'file': file_content,
            'file_name': 'Timesheet Report.xlsx'
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
        report_common_method.update_summary_and_emp_lists(
            self.env,
            calendar_event,
            fromdate,
            todate,
            self.month_data,
        )

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(self.env.ref('prime4_report.visit_summary_report_view').id, 'form')],
            'res_model': 'visit.summary.report',
            'target': 'new',
            'context': self._context
        }
