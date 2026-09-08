from odoo import models, fields, api, _
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
from odoo.exceptions import UserError
from odoo.addons.project_management import report_common_method


class EneicoSummaryReport(models.TransientModel):
    _name = 'eneico.summary.report'
    _inherit = 'common.report'
    _description = 'Eneico Timesheet Report'

    def generate_report_excel(self):

        domain, fromdate, todate = self._get_calendar_domain(
            client_code='eneico',
            include_status=False,
            extra_domain=[]
        )

        calendar_event = self.env['calendar.event'].search(domain, order="start")
        if not calendar_event:
            raise UserError(_("No Record Found"))

        def eneico_value_builder(record):
            values = self._build_common_values(record)

            values.update({
                'abortive_visit': record.abortive_visit,
                'kms_new': record.kms or '',
                'hrs_new': record.hrs or '',
                'approver': record.approver.name if record.approver else '',
            })

            return values

        start_values_data = self._group_calendar_records(
            calendar_event, eneico_value_builder
        )

        total_hrs = 0
        total_abortive = 0
        totol_fullday = 0
        totol_halfday = '-'
        start_values_data_sort = sorted(start_values_data.items())
        data = []
        for start, categorious in start_values_data_sort:
            for category, records in categorious.items():
                uni = []
                byte_io = BytesIO()
                workbook = xlsxwriter.Workbook(byte_io)
                worksheet = workbook.add_worksheet(category)
                worksheet.set_column('A:A', 17)
                worksheet.set_column('B:B', 12)
                worksheet.set_column('C:C', 12)
                worksheet.set_column('D:D', 12)
                worksheet.set_column('E:E', 24)

                worksheet.set_row(7, 30)
                worksheet.set_row(8, 30)
                worksheet.set_row(9, 30)
                worksheet.set_row(10, 30)
                worksheet.set_row(11, 30)

                style_header_new_no_line = workbook.add_format(
                    {'bold': True, 'font_size': 8, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True})

                style_header_left1 = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 10, 'align': 'left', 'valign': 'vcenter',
                     'text_wrap': True, 'bg_color': '#FF9900', 'border': 1})
                style_header2 = workbook.add_format(
                    {'bold': True, 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'bg_color': '#99CCFF', 'border': 1})
                style_center_align = workbook.add_format(
                    {'font_name': 'Calibri', 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})
                style_center_align_wrap = workbook.add_format(
                    {'font_name': 'Calibri', 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})
                style_header = workbook.add_format(
                    {'bold': True, 'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})
                style_header1 = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter',
                     'text_wrap': True, 'bg_color': '#FF9900', 'border': 1})
                style_header_left = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 10, 'align': 'left', 'valign': 'vcenter',
                     'text_wrap': True, 'border': 1})
                style_left_align = workbook.add_format(
                    {'font_name': 'Calibri', 'font_size': 11, 'align': 'left', 'valign': 'vcenter', 'border': 1, 'text_wrap': True})

                row = 0
                worksheet.merge_range(row, 0, row, 4, '', style_header_new_no_line)
                row = 1
                worksheet.merge_range(row, 0, row, 4, '', style_header_new_no_line)
                row = 2
                worksheet.merge_range(row, 0, row, 4, '', style_header_new_no_line)
                row = 3
                worksheet.merge_range(row, 0, row, 4, '', style_header_new_no_line)
                row = 4
                worksheet.merge_range(row, 0, row, 4, '', style_header_new_no_line)
                row = 5
                worksheet.merge_range(row, 0, row, 4, '', style_header_new_no_line)
                row = 6
                worksheet.merge_range(row, 0, row, 4, '', style_header_new_no_line)

                row = 8

                worksheet.merge_range(row, 0, row, 4, 'Project Name : ' + self.project_id.name, style_header_left1)

                row = 10
                worksheet.merge_range(row, 0, row, 4, 'Name of the Vendor : ' + start.split('_')[0], style_header_left1)

                row += 1
                worksheet.write(row, 0, 'Inspection Visit Date', style_header2)
                worksheet.write(row, 1, 'Day', style_header2)
                worksheet.write(row, 2, 'No.of Hours', style_header2)
                worksheet.write(row, 3, 'Kms', style_header2)
                worksheet.write(row, 4, 'Report No.', style_header2)
                end_row = row
                row1 = row
                totol_fullday += 1
                unique = ''
                po_value = []
                for val in records:
                    purchae_value = str(val['purchase'])
                    if purchae_value not in po_value:
                        po_value.append(purchae_value)
                    un = val['unique_no']
                    txn = val['txn']
                    part = str(un) if un else str(txn)
                    if part not in uni:
                        uni.append(part)
                        unique += str(part) + '_'
                    row += 1
                    row1 += 1

                    worksheet.write(row, 0, val['start'], style_center_align)
                    if calendar_event[0]:
                        if calendar_event[0].start:
                            calendar_start_day = datetime.strptime(val['start'], "%d-%m-%Y").strftime(
                                "%A")
                        else:
                            calendar_start_day = ''
                        worksheet.write(row, 1, calendar_start_day, style_center_align_wrap)
                    else:
                        worksheet.write(row, 1, '', style_header1)

                    if not val['abortive_visit']:

                        worksheet.write(row, 2, val['hrs_new'], style_center_align)
                        total_hrs += val['days']
                    elif val['abortive_visit']:

                        worksheet.write(row, 2, 'Abortive', style_center_align)
                        total_abortive += val['days']
                    else:
                        worksheet.write(row, 2, '', style_center_align)
                    worksheet.write(row, 3, val['kms_new'], style_center_align_wrap)
                    worksheet.write(row, 4, val['number'], style_center_align)

                end_row = row1
                next_row1 = end_row + 1
                worksheet.write(next_row1, 0, '', style_header)
                worksheet.write(next_row1, 1, '', style_header)
                worksheet.write(next_row1, 2, '', style_header)
                worksheet.write(next_row1, 3, '', style_header)
                worksheet.write(next_row1, 4, '', style_left_align)
                next_row = next_row1 + 1
                worksheet.merge_range(next_row, 0, next_row, 1, 'No of Full Days Worked', style_header_left)
                worksheet.merge_range(next_row, 2, next_row, 4, str(total_hrs), style_header_left)
                next1_row = next_row + 1
                worksheet.merge_range(next1_row, 0, next1_row, 1, 'No of Abortive Days', style_header_left)
                worksheet.merge_range(next1_row, 2, next1_row, 4, str(total_abortive), style_header_left)
                next12_row = next1_row + 1
                worksheet.merge_range(next12_row, 0, next12_row, 4, str(''), style_header_left)
                next2_row = next12_row + 1
                worksheet.set_row(next2_row, 50)
                worksheet.merge_range(next2_row, 0, next2_row, 1, 'Name of Inspector : ' + start.split('_')[-1],
                                   style_header_left)
                if self.inspector_id.employee_signature:
                    worksheet.merge_range(next2_row, 2, next2_row, 4, 'Signature:', style_header_left)

                    # worksheet.insert_bitmap('imagetoadd1.bmp', next2_row, 3, 4, scale_x=0.9, scale_y=.2, y=2.5)
                else:
                    worksheet.merge_range(next2_row, 2, next2_row, 4, 'Signature:', style_header_left)

                next13_row = next2_row + 1
                worksheet.merge_range(next13_row, 0, next13_row, 4, '')

                next3_row = next13_row + 1
                worksheet.set_row(next3_row, 50)

                worksheet.merge_range(next3_row, 0, next3_row, 1, 'Name of Approving Authority :' + val['approver'],
                                   style_header_left)
                worksheet.merge_range(next3_row, 2, next3_row, 4, 'Signature:', style_header_left)

                row = 7
                if calendar_event[0]:
                    if calendar_event[0].start:
                        calendar_start_date = calendar_event[0].start.strftime("%b-%Y")
                    else:
                        calendar_start_date = ''
                    worksheet.merge_range(row, 0, row, 4, 'Summary of Timesheet - ' + calendar_start_date, style_header1)
                else:
                    worksheet.write(4, 4, '', style_header1)

                row = 9

                if len(po_value) > 0:
                    po_numbers = ','.join(po_value)
                else:
                    po_numbers = ''
                worksheet.merge_range(row, 0, row, 4, 'PO Number : ' + po_numbers, style_header_left1)

                workbook.close()
                file_data = byte_io.getvalue()
                file_content = base64.b64encode(file_data)
                data.append(('%s_%s_%s.xlsx' % (unique, start, category), file_content))

        self._create_zip_from_xlsx_data(data)

        report_common_method.send_report_notification(
            self.env,
            self.file_name,
            self.file,
            'eneico.summary.report',
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
            'views': [(self.env.ref('project_management.view_common_report').id, 'form')],
            'res_model': 'eneico.summary.report',
            'target': 'new',
            'context': self._context
        }
