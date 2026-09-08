from odoo import models, fields, api, _
import base64
from io import BytesIO
import xlsxwriter
from odoo.exceptions import UserError
from odoo.tools.misc import file_path as get_file_path
from odoo.addons.project_management import report_common_method


class VisitSummaryReport2(models.TransientModel):
    _name = 'visit.summary.report2'
    _inherit = 'common.report'
    _description = 'Timesheet Report'

    role_id = fields.Many2one('p4.employee.role', string="Role")
    initiator_id = fields.Many2one('client.initiator', string="Initiator")


    def generate_report_excel(self):
        domain, fromdate, todate = self._get_calendar_domain(
            client_code='TCM',
            include_status=True,
            extra_domain=[
                ('employee_role', '=', self.role_id.id) if self.role_id else (),
                ('initiator_id', '=', self.initiator_id.id) if self.initiator_id else (),
            ]
        )
        calendar_event = self.env['calendar.event'].search(domain, order="start")
        if not calendar_event:
            raise UserError(_("No Record Found"))

        def tcm_value_builder(record):
            values = self._build_common_values(record)
            category_label = dict(record._fields['category_expenses'].selection).get(record.category_expenses, '')
            values.update({
                'eigl_person': record.eigl_person_id.name if record.eigl_person_id else '',
                'overnight': (
                    'Overnight Expenses'
                    if record.overnight_expense
                    else 'No Overnight Expenses'
                ),
                'halfday': '-',
                'notification_no': record.notification_no if record.notification_no else '',
                'role': f"{record.employee_role.name if record.employee_role else ''}\n{category_label}",
            })

            return values

        start_values_data = self._group_calendar_records(
            calendar_event, tcm_value_builder
        )


        totol_halfday = '-'
        start_values_data_sort = sorted(start_values_data.items())
        data = []
        for start, categorious in start_values_data_sort:
            for category, records in categorious.items():
                byte_io = BytesIO()
                workbook = xlsxwriter.Workbook(byte_io)
                po_value = []
                worksheet = workbook.add_worksheet(category)

                worksheet.set_column('A:A', 8)
                worksheet.set_column('B:B', 23)
                worksheet.set_column('C:C', 15)
                worksheet.set_column('D:D', 15)
                worksheet.set_column('E:E', 10)
                worksheet.set_column('F:F', 16)
                worksheet.set_column('G:G', 16)
                worksheet.set_column('H:H', 13)
                worksheet.set_column('I:I', 3)
                worksheet.set_column('J:J', 3)
                worksheet.set_column('K:K', 7)
                worksheet.set_column('L:L', 17)

                style_header = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})
                style_header2 = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'bg_color': '#ffffcc', 'border': 1})
                style_header_new = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})
                style_header_new_left = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 8, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})
                style_header_new_right = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 8, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})
                style_center_align = workbook.add_format(
                    {'font_name': 'Arial', 'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'text_wrap': True})
                style_center_align_wrap = workbook.add_format(
                    {'font_name': 'Arial', 'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1})

                image_path = get_file_path('prime4_report/static/src/img/logo.jpg')
                with open(image_path, 'rb') as f:
                    img_bytes = BytesIO(f.read())

                img_bytes.seek(0)
                worksheet.set_row(0, 75)
                worksheet.insert_image(0, 0, 'logo.jpg', {
                    'image_data': img_bytes,
                    'x_scale': 0.6,
                    'y_scale': 0.6,
                    'x_offset': 4,
                    'y_offset': 2,
                })


                company = self.env['res.company'].search([])[0]
                image = self.env.user.company_id.logo

                row = 3
                worksheet.write(row, 4, 'Contract', style_header)
                if self.role_id.name == 'inspector':
                    if self.project_id.inspection_contract_no:
                        worksheet.write(row, 5, self.project_id.inspection_contract_no, style_header2)
                    else:
                        worksheet.write(row, 5, '', style_header2)
                elif self.role_id.name == 'expeditor':
                    if self.project_id.expediting_contract_no:
                        worksheet.write(row, 5, self.project_id.expediting_contract_no, style_header2)
                    else:
                        worksheet.write(row, 5, '', style_header2)
                else:
                    if self.project_id.inspection_contract_no:
                        worksheet.write(row, 5, self.project_id.inspection_contract_no, style_header2)
                    else:
                        worksheet.write(row, 5, '', style_header2)

                worksheet.merge_range(row, 7, row, 8, 'Month', style_header_new_left)
                row = 4
                worksheet.write(row, 0, 'Agency', style_header_new)
                worksheet.write(row, 1, company.name, style_header2)
                worksheet.merge_range(row, 7, row, 8, 'Country', style_header_new_left)
                row = 5
                row += 1
                worksheet.write(row, 0, 'P.O. Nr.', style_header)
                worksheet.write(row, 1, 'VENDOR', style_header)
                worksheet.write(row, 2, 'INSPECTOR', style_header)
                worksheet.write(row, 3, 'ROLE', style_header)
                worksheet.write(row, 4, 'VISIT DATE', style_header)
                worksheet.write(row, 5, 'REPORT NUMBER', style_header)
                worksheet.write(row, 6, 'NOTIFICATION NO', style_header)
                worksheet.write(row, 7, 'EICM', style_header)
                worksheet.merge_range(row, 8, row, 9, '', style_header2)
                worksheet.write(row, 10, 'Expenses \nEUR', style_header)
                worksheet.write(row, 11, 'Expenses \nDescription', style_header)

                row += 1
                worksheet.write(row, 0, '', style_header)
                worksheet.write(row, 1, '', style_header)
                worksheet.write(row, 2, '', style_header)
                worksheet.write(row, 3, '', style_header)
                worksheet.write(row, 4, '', style_header)
                worksheet.write(row, 5, '', style_header)
                worksheet.write(row, 6, '', style_header)
                worksheet.write(row, 7, '', style_header)
                worksheet.write(row, 8, 'OD', style_header2)
                worksheet.write(row, 9, 'HD', style_header2)
                worksheet.write(row, 10, '', style_header)
                worksheet.write(row, 11, '', style_header)
                end_row = row
                totol_fullday = 0
                unique = []
                uniqueno = ''
                count = 0
                for val in records:
                    count += 1
                    totol_fullday += val['days'] or 0
                    row += 1
                    po = val['purchase']
                    if po not in po_value:
                        po_value.append(val['purchase'])
                    un = val['unique_no']
                    txn = val['txn']
                    part = str(un) if un else str(txn)
                    if part not in unique:
                        unique.append(part)
                        uniqueno += part + '_'

                    worksheet.write(row, 0, val['purchase'], style_center_align_wrap)
                    worksheet.write(row, 1, val['vendor'], style_center_align_wrap)
                    worksheet.write(row, 2, val['employee'], style_center_align)
                    worksheet.write(row, 3, val['role'], style_center_align)
                    worksheet.write(row, 4, val['start'], style_center_align)
                    worksheet.write(row, 5, val['number'], style_center_align)
                    worksheet.write(row, 6, val['notification_no'], style_center_align)
                    worksheet.write(row, 7, val['eigl_person'], style_center_align)
                    worksheet.write(row, 8, val['days'], style_center_align)
                    worksheet.write(row, 9, '-', style_center_align)
                    worksheet.write(row, 10, '-', style_center_align)
                    worksheet.write(row, 11, val['overnight'], style_center_align)


                end_row = row
                next_row = end_row + 1
                worksheet.write(next_row, 0, '', style_header)
                worksheet.write(next_row, 1, '', style_header)
                worksheet.write(next_row, 2, '', style_header)
                worksheet.write(next_row, 3, '', style_header)
                worksheet.write(next_row, 4, '', style_header)
                worksheet.write(next_row, 5, '', style_header)
                worksheet.write(next_row, 6, '', style_header)
                worksheet.write(next_row, 7, '', style_header)

                worksheet.write(next_row, 8, str(totol_fullday), style_center_align)
                worksheet.write(next_row, 9, str(totol_halfday), style_center_align)

                worksheet.write(next_row, 10, '', style_header)
                worksheet.write(next_row, 11, '', style_header)

                if calendar_event[0]:
                    if calendar_event[0].start:
                        calendar_start_date = calendar_event[0].start.strftime("%b-%Y")
                    else:
                        calendar_start_date = ''
                    worksheet.write(3, 6, calendar_start_date, style_header_new_right)
                else:
                    worksheet.write(3, 6, '', style_header_new_right)

                if len(po_value) > 0:
                    po_numbers = ','.join(po_value)
                else:
                    po_numbers = ''
                data_project = str(self.project_id.name) + '; PO# ' + str(po_numbers)

                worksheet.write(4, 4, 'Project', style_header_new)
                worksheet.write(4, 5, data_project, style_header_new)
                worksheet.write(4, 6, calendar_event[0].v_location.name, style_header_new_right)

                # Save the file in memory
                workbook.close()
                file_data = byte_io.getvalue()
                file_content = base64.b64encode(file_data)
                data.append(('%s_%s_%s.xlsx' % (uniqueno, start, category), file_content))

        self._create_zip_from_xlsx_data(data)

        report_common_method.send_report_notification(
            self.env,
            self.file_name,
            self.file,
            'visit.summary.report2',
            self.id,
            group_xmlid='project_management.accounts_role',
            body='Report Has been Generated. Kindly Review it !'
        )
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
            'views': [(self.env.ref('prime4_report.visit_summary_report_view2').id, 'form')],
            'res_model': 'visit.summary.report2',
            'target': 'new',
            'context': self._context
        }
