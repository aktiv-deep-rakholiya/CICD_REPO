from odoo import models, fields, api, _
import base64
from io import BytesIO
import xlsxwriter
from odoo.exceptions import UserError
from odoo.tools.misc import file_path as get_file_path
from odoo.addons.project_management import report_common_method


class PetrofacTurkSummaryReport(models.TransientModel):
    _name = 'petrofac.turk.summary.report'
    _inherit = 'common.report'
    _description = 'Petrofac Timesheet Report'

    service_no = fields.Many2many(related='project_id.service_order_no_ids', string="Service Number")

    def generate_report_excel(self):

        domain, fromdate, todate = self._get_calendar_domain(
            client_code='petrofac',
            include_status=True,
            extra_domain=[]
        )

        calendar_event = self.env['calendar.event'].search(domain, order="date")
        if not calendar_event:
            raise UserError(_("No Record Found"))

        def petrofac_value_builder(record):
            values = self._build_common_values(record)

            values.update({
                'abortive_visit': record.abortive_visit,
                "extra_hrs_new": record.extra_hrs or "",
                'kms_new': record.kms or '',
                'approver': record.approver.name if record.approver else '',
            })

            return values

        start_values_data = self._group_calendar_records(
            calendar_event, petrofac_value_builder
        )

        start_values_data_sort = sorted(start_values_data.items())
        data = []
        totol_fullday = 0
        totol_halfday = '-'
        for start, categorious in start_values_data_sort:

            for category, records in categorious.items():
                byte_io = BytesIO()
                workbook = xlsxwriter.Workbook(byte_io)
                worksheet = workbook.add_worksheet(category)
                
                worksheet.set_column('A:A', 13)
                worksheet.set_column('B:B', 16)
                worksheet.set_column('C:C', 18)
                worksheet.set_column('D:D', 18)
                worksheet.set_column('E:E', 18)
                worksheet.set_column('F:F', 24)
                worksheet.set_column('G:G', 7)
                worksheet.set_column('H:H', 7)
                worksheet.set_column('I:I', 7)
                worksheet.set_column('J:J', 7)
                worksheet.set_column('K:K', 7)
                worksheet.set_column('L:L', 6)

                worksheet.fit_to_pages(1, 1)
                worksheet.set_landscape()

                style_header_new_no_line = workbook.add_format(
                    {'bold': True, 'font_size': 8, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True})
                style_header_left = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 10, 'align': 'left', 'valign': 'vcenter',
                     'text_wrap': True, 'border': 1})
                style_header2 = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'bg_color': '#99CCFF', 'border': 1})
                style_center_align = workbook.add_format(
                    {'font_name': 'Calibri', 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'text_wrap': True})
                style_center_align_wrap = workbook.add_format(
                    {'font_name': 'Calibri', 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})
                style_header = workbook.add_format(
                    {'bold': True, 'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})
                style_left_align = workbook.add_format(
                    {'font_name': 'Calibri', 'font_size': 11, 'align': 'left', 'valign': 'vcenter', 'border': 1, 'text_wrap': True})
                style_left_align_color = workbook.add_format(
                    {'font_name': 'Calibri', 'font_size': 11, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True,
                     'bg_color': '#99CCFF', 'border': 1})
                style_header1 = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter',
                     'text_wrap': True, 'border': 1})

                image_path = get_file_path('petrofac_report/static/src/img/logo.jpg')
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
                
                row = 0

                row = 1
                worksheet.merge_range(row, 0, row, 10, '', style_header_new_no_line)
                row = 2
                worksheet.merge_range(row, 0, row, 10, '', style_header_new_no_line)
                row = 3
                worksheet.merge_range(row, 0, row, 10, '', style_header_new_no_line)
                row = 4
                worksheet.merge_range(row, 0, row, 10, '', style_header_new_no_line)
                row = 5
                worksheet.merge_range(row, 0, row, 10, '', style_header_new_no_line)

                row = 7
                worksheet.write(row, 0, 'Service Order Number With Petrofac', style_header_left)
                worksheet.merge_range(row, 1, row, 10, self.service_no.name if self.service_no.name else "",
                                   style_header_left)

                row = 8
                worksheet.write(row, 0, 'Name of Inspector', style_header_left)
                worksheet.merge_range(row, 1, row, 10, str(start.split('_')[-1]), style_header_left)

                row += 1
                worksheet.write(row, 0, 'Dates', style_header2)
                worksheet.write(row, 1, 'PO No', style_header2)
                worksheet.write(row, 2, 'Vendor', style_header2)
                worksheet.write(row, 3, 'Location', style_header2)
                worksheet.write(row, 4, 'Role', style_header2)
                worksheet.write(row, 5, 'Report Number', style_header2)
                worksheet.write(row, 6, 'Days', style_header2)
                worksheet.write(row, 7, 'Extra Hrs', style_header2)
                worksheet.write(row, 8, 'Amount', style_header2)
                worksheet.write(row, 9, 'Kms', style_header2)
                worksheet.write(row, 10, 'Rate', style_header2)
                end_row = row
                row1 = row
                totol_fullday += 1
                unique = ''
                uni = []
                total = 0
                total_abortive = 0

                for val in records:
                    un = val['unique_no']
                    txn = val['txn']
                    part = str(un) if un else str(txn)
                    if part not in uni:
                        uni.append(part)
                        unique += str(part) + '_'
                    row += 1
                    row1 += 1
                    worksheet.write(row, 0, val['start'], style_center_align)
                    worksheet.write(row, 1, val['purchase'], style_center_align_wrap)
                    worksheet.write(row, 2, val['vendor'], style_center_align_wrap)
                    worksheet.write(row, 3, calendar_event[0].v_location.name, style_center_align_wrap)
                    worksheet.write(row, 4, val['category'], style_center_align_wrap)
                    worksheet.write(row, 5, val['number'], style_center_align)

                    if val['allday']:

                        worksheet.write(row, 6, val['days'], style_center_align)
                        total += val['days'] if val['days'] else 0
                    elif val['abortive_visit']:

                        worksheet.write(row, 6, 'Abortive', style_center_align)
                        total_abortive += 1
                    else:
                        worksheet.write(row, 6, 0.5, style_center_align)
                        total += 0.5

                    worksheet.write(row, 7, val['extra_hrs_new'], style_center_align)

                    worksheet.write(row, 8, '', style_center_align)

                    worksheet.write(row, 9, val['kms_new'], style_center_align)

                    worksheet.write(row, 10, '', style_center_align)
                    end_row = row1

                next_row1 = end_row + 1
                worksheet.write(next_row1, 0, '', style_header)
                worksheet.write(next_row1, 1, '', style_header)
                worksheet.write(next_row1, 2, '', style_header)
                worksheet.write(next_row1, 3, '', style_header)
                worksheet.write(next_row1, 4, '', style_header)
                worksheet.write(next_row1, 5, '', style_left_align)

                worksheet.write(next_row1, 6, '', style_center_align)
                worksheet.write(next_row1, 7, '', style_center_align)
                worksheet.write(next_row1, 8, '', style_center_align)
                worksheet.write(next_row1, 9, '', style_center_align)
                worksheet.write(next_row1, 10, '', style_center_align)

                next_row = next_row1 + 1
                worksheet.write(next_row, 0, '', style_header)
                worksheet.write(next_row, 1, '', style_header)
                worksheet.write(next_row, 2, '', style_header)
                worksheet.write(next_row, 3, '', style_header)
                worksheet.write(next_row, 4, '', style_header)
                worksheet.write(next_row, 5, 'Total', style_left_align)

                worksheet.write(next_row, 6, str(total), style_center_align)
                worksheet.write(next_row, 7, '', style_center_align)
                worksheet.write(next_row, 8, '', style_center_align)
                worksheet.write(next_row, 9, '', style_center_align)
                worksheet.write(next_row, 10, '', style_center_align)

                next1_row = next_row + 1
                worksheet.write(next1_row, 0, 'Daily Rate', style_left_align_color)
                worksheet.write(next1_row, 1, '', style_header)
                worksheet.write(next1_row, 2, '', style_header)
                worksheet.write(next1_row, 3, '', style_header)
                worksheet.write(next1_row, 4, '', style_header)
                worksheet.write(next1_row, 5, 'Abortive Total', style_left_align)

                worksheet.write(next1_row, 6, str(total_abortive), style_center_align)
                worksheet.write(next1_row, 7, '', style_center_align)
                worksheet.write(next1_row, 8, '', style_center_align)
                worksheet.write(next1_row, 9, '', style_center_align)
                worksheet.write(next1_row, 10, '', style_center_align)

                next2_row = next1_row + 1
                worksheet.write(next2_row, 0, 'KM Rate(Above 100 KM):', style_left_align_color)
                worksheet.write(next2_row, 1, '', style_header)
                worksheet.write(next2_row, 2, '', style_header)
                worksheet.write(next2_row, 3, '', style_header)
                worksheet.write(next2_row, 4, '', style_header)
                worksheet.write(next2_row, 5, 'Total Invoice Amount', style_left_align_color)

                worksheet.write(next2_row, 6, '', style_center_align)
                worksheet.write(next2_row, 7, '', style_center_align)
                worksheet.write(next2_row, 8, '', style_center_align)
                worksheet.write(next2_row, 9, '', style_center_align)
                worksheet.write(next2_row, 10, '', style_center_align)

                next3_row = next2_row + 1
                worksheet.merge_range(next3_row, 0, next3_row, 1, 'Name of Approving Authority:', style_header_left)
                worksheet.merge_range(next3_row, 2, next3_row, 4, val['approver'], style_header_left)

                worksheet.write(next3_row, 5, '', style_header)

                worksheet.merge_range(next3_row, 6, next3_row, 10, 'Signature of Approving Authority:',
                                   style_header_left)

                next4_row = next3_row + 1
                worksheet.write(next4_row, 0, 'Date:', style_header_left)
                worksheet.write(next4_row, 1, '', style_header)
                worksheet.write(next4_row, 2, '', style_header)
                worksheet.write(next4_row, 3, '', style_header)
                worksheet.write(next4_row, 4, '', style_header)
                worksheet.write(next4_row, 5, '', style_header)

                worksheet.write(next4_row, 6, '', style_center_align)
                worksheet.write(next4_row, 7, '', style_center_align)
                worksheet.write(next4_row, 8, '', style_center_align)
                worksheet.write(next4_row, 9, '', style_center_align)
                worksheet.write(next4_row, 10, '', style_center_align)

                row = 6
                if calendar_event[0]:
                    if calendar_event[0].start:
                        calendar_start_date = calendar_event[0].start.strftime("%b-%Y")
                    else:
                        calendar_start_date = ''
                    worksheet.merge_range(row, 0, row, 10, 'Timesheet for the month of ' + calendar_start_date,
                                       style_header1)
                else:
                    worksheet.write(5, 5, '', style_header1)

                # Save the file in memory
                workbook.close()
                file_data = byte_io.getvalue()
                file_content = base64.b64encode(file_data)
                data.append(('%s_%s_%s.xlsx' % (unique, start, category), file_content))

        self._create_zip_from_xlsx_data(data)

        report_common_method.send_report_notification(
            self.env,
            self.file_name,
            self.file,
            'petrofac.turk.summary.report',
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
            'views': [(self.env.ref('petrofac_report.petrofac_turk_summary_report_view').id, 'form')],
            'res_model': 'petrofac.turk.summary.report',
            'target': 'new',
            'context': self._context
        }
