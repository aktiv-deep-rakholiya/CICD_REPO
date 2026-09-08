from odoo import models, fields, api, _
import base64
from io import BytesIO
import xlsxwriter
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.misc import file_path as get_file_path
from odoo.addons.project_management import report_common_method


class ApplusSummaryReport(models.TransientModel):
    _name = 'applus.summary.report'
    _inherit = 'common.report'
    _description = 'Applus Velosi Report'

    date_submit = fields.Date(string='Submission Date')

    def generate_report_excel(self):

        domain, fromdate, todate = self._get_calendar_domain(
            client_code='applus',
            include_status=False,
            extra_domain=[]
        )

        calendar_event = self.env['calendar.event'].search(domain, order="start")
        if not calendar_event:
            raise UserError(_("No Record Found"))

        def applus_value_builder(record):
            values = self._build_common_values(record)

            values.update({
                'pscjob': record.pscjob or '',
                'job_assign': record.job_assign or '',
                'kms_new': record.add_km_mileage1 or '',
                'v_location': record.v_location.name,
            })

            return values

        start_values_data = self._group_calendar_records(
            calendar_event, applus_value_builder
        )


        totol_fullday = 0
        totol_halfday = '-'
        start_values_data_sort = sorted(start_values_data.items())
        data = []
        for start, categorious in start_values_data_sort:
            for category, records in categorious.items():
                output = BytesIO()
                workbook = xlsxwriter.Workbook(output)
                sheet1 = workbook.add_worksheet(category)

                style_header = workbook.add_format(
                    {'bold': True, 'font_size': 8, 'font_name': 'Times New Roman', 'text_wrap': 1, 'align': 'center',
                     'valign': 'vcenter', 'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_header_new_no_line = workbook.add_format(
                    {'bold': True, 'font_size': 12, 'font_name': 'Times New Roman',
                     'align': 'center', 'valign': 'vcenter', 'text_wrap': 1, 'font_color': '#3339FF'})

                style_header2 = workbook.add_format({'bold': True, 'font_size': 10, 'font_name': 'Times New Roman',
                                                     'align': 'center', 'valign': 'vcenter', 'right': 1, 'top': 1,
                                                     'left': 1, 'bottom': 1, 'text_wrap': 1})

                style_header22 = workbook.add_format({'bold': True, 'font_size': 10, 'font_name': 'Times New Roman',
                                                      'align': 'left', 'valign': 'top', 'right': 1, 'top': 1, 'left': 1,
                                                      'bottom': 1, 'text_wrap': 1})


                style_center_align = workbook.add_format(
                    {'bold': False, 'font_size': 10, 'font_name': 'Times New Roman',
                     'align': 'center', 'valign': 'vcenter', 'text_wrap': 1,
                     'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_center_align_wrap = workbook.add_format(
                    {'bold': False, 'font_size': 10, 'font_name': 'Times New Roman',
                     'align': 'center', 'valign': 'vcenter', 'text_wrap': 1, 'right': 1, 'left': 1, 'top': 1,
                     'bottom': 1})

                sheet1.set_column(0, 0, 11.00)
                sheet1.set_column(1, 1, 10.00)
                sheet1.set_column(2, 2, 12.00)
                sheet1.set_column(3, 3, 12.00)
                sheet1.set_column(4, 4, 12.00)
                sheet1.set_column(5, 5, 8.00)
                sheet1.set_column(6, 12, 9.00)
                sheet1.set_column(13, 13, 1.00)
                sheet1.set_column(14, 14, 55.00)

                sheet1.set_row(0, 50)

                sheet1.fit_to_pages(1, 0)
                sheet1.set_landscape()
                sheet1.header_str = ''
                sheet1.footer_str = ''
                sheet1.set_row(0, 70)

                image_path = get_file_path('petrofac_report/static/src/img/applus.jpg')
                with open(image_path, 'rb') as f:
                    img_bytes = BytesIO(f.read())

                img_bytes.seek(0)

                sheet1.set_row(0, 50)
                sheet1.insert_image(0, 0, 'applus.jpg', {
                    'image_data': img_bytes,
                    'x_scale': 0.3,
                    'y_scale': 0.4,
                    'x_offset': 4,
                    'y_offset': 4,
                })
                row = 0
                sheet1.merge_range(row, 0, row, 12,
                                   'APPLUS ITALY s.r.l.\nVia Cinquantenario, 8  -  24044 Dalmine (BG) Italy\nC.F. / P.I. 02940940162',
                                   style_header_new_no_line)

                row = 2
                sheet1.merge_range(row, 0, row, 1, 'Inspector', style_header2)
                sheet1.merge_range(row, 2, row, 6, start.split('_')[-1], style_header2)
                sheet1.merge_range(row, 9, row, 12, 'RATE', style_header2)
                if self.date_submit:
                    start_date_format = datetime.strptime(str(self.date_submit), "%Y-%m-%d").strftime("%d-%m-%Y")
                    start_date = start_date_format

                    row = 3
                    sheet1.merge_range(row, 0, row, 1, 'Date', style_header2)
                    sheet1.merge_range(row, 2, row, 6, start_date, style_header2)
                    sheet1.merge_range(row, 9, row, 10, 'Half Day', style_header2)
                    sheet1.merge_range(row, 11, row, 12, '', style_header2)

                row = 4
                sheet1.merge_range(row, 0, row, 1, 'Proposal no.', style_header2)
                sheet1.merge_range(row, 2, row, 6, '', style_header2)
                sheet1.merge_range(row, 9, row, 10, 'Full Day', style_header2)
                sheet1.merge_range(row, 11, row, 12, '', style_header2)

                row = 5
                sheet1.merge_range(row, 9, row, 10, 'Km', style_header2)
                sheet1.merge_range(row, 11, row, 12, '', style_header2)

                row = 8
                sheet1.merge_range(row, 0, row, 4, '')
                sheet1.write(row, 5, 'TOTAL', style_header2)
                sheet1.write(row, 6, 'Mon', style_header2)
                sheet1.write(row, 7, 'Tue', style_header2)
                sheet1.write(row, 8, 'Wed', style_header2)
                sheet1.write(row, 9, 'Thu', style_header2)
                sheet1.write(row, 10, 'Fri', style_header2)
                sheet1.write(row, 11, 'Sat', style_header2)
                sheet1.write(row, 12, 'Sun', style_header2)
                sheet1.write(row, 13, '', style_header2)
                sheet1.merge_range(row, 14, 22, 14,
                                   'The Time & Expenses Form MUST be submitted with the visit reports\nInstructions for filling in the form:\n-Fill in only the yellow cells\n-Row 10: Fill in the date under the Week day\n-Row 11: Indicate F for full days or H for half day\n-Row 12: Indicate km spent\n-Row 14: Indicate the cost of air ticket (if any)\n-Row 15: Indicate the cost of lodging (if any)\n-Row 16: Indicate the cost of auto/train/taxi (if any)\n-Row from 23 : Indicate the JA (Job Assignment); PSC Job (indicated in \nthe JA) and P.O.number. Under percentage of working time you will proceed\nas follows: in case of one P.O. you will indicate 100%; in case of two or more\nP.O.s handled in the same day you will split the % of time dedicated for each\norder; the total must be equal to 100% (example: in case of 3 Orders you may\nhave 20% of time on the first P.O., 50% of time on the second P.O. and 30%\nof time on the third P.O.; Total 100%)\n-Row 46: For Inspectors comments (if any)',
                                   style_header22)

                row = 9
                sheet1.merge_range(row, 0, row, 1, '')
                sheet1.merge_range(row, 2, row, 4, 'Date', style_header2)
                sheet1.write(row, 5, '', style_header2)

                row = 12
                sheet1.merge_range(row, 0, row, 1, '')
                sheet1.merge_range(row, 2, row, 4, '', style_header2)
                sheet1.write(row, 5, '', style_header2)
                sheet1.write(row, 6, '', style_header2)
                sheet1.write(row, 7, '', style_header2)
                sheet1.write(row, 8, '', style_header2)
                sheet1.write(row, 9, '', style_header2)
                sheet1.write(row, 10, '', style_header2)
                sheet1.write(row, 11, '', style_header2)
                sheet1.write(row, 12, '', style_header2)

                row = 13
                sheet1.merge_range(row, 0, row, 1, '')
                sheet1.merge_range(row, 2, row, 4, 'Airfare (*)', style_header2)
                sheet1.write(row, 5, '-', style_header2)
                sheet1.write(row, 6, '', style_header2)
                sheet1.write(row, 7, '', style_header2)
                sheet1.write(row, 8, '', style_header2)
                sheet1.write(row, 9, '', style_header2)
                sheet1.write(row, 10, '', style_header2)
                sheet1.write(row, 11, '', style_header2)
                sheet1.write(row, 12, '', style_header2)

                row = 14
                sheet1.merge_range(row, 0, row, 1, '')
                sheet1.merge_range(row, 2, row, 4, 'Lodging (*)', style_header2)
                sheet1.write(row, 5, '-', style_header2)
                sheet1.write(row, 6, '', style_header2)
                sheet1.write(row, 7, '', style_header2)
                sheet1.write(row, 8, '', style_header2)
                sheet1.write(row, 9, '', style_header2)
                sheet1.write(row, 10, '', style_header2)
                sheet1.write(row, 11, '', style_header2)
                sheet1.write(row, 12, '', style_header2)

                row = 15
                sheet1.merge_range(row, 0, row, 1, '')
                sheet1.merge_range(row, 2, row, 4, 'Auto/train/taxi (*)', style_header2)
                sheet1.write(row, 5, '-', style_header2)
                sheet1.write(row, 6, '', style_header2)
                sheet1.write(row, 7, '', style_header2)
                sheet1.write(row, 8, '', style_header2)
                sheet1.write(row, 9, '', style_header2)
                sheet1.write(row, 10, '', style_header2)
                sheet1.write(row, 11, '', style_header2)
                sheet1.write(row, 12, '', style_header2)

                row = 16
                sheet1.merge_range(row, 0, row, 1, '')
                sheet1.merge_range(row, 2, row, 4, 'TOTAL TO BE INVOICED', style_header2)
                sheet1.write(row, 5, '-', style_header2)
                sheet1.write(row, 6, '', style_header2)
                sheet1.write(row, 7, '', style_header2)
                sheet1.write(row, 8, '', style_header2)
                sheet1.write(row, 9, '', style_header2)
                sheet1.write(row, 10, '', style_header2)
                sheet1.write(row, 11, '', style_header2)
                sheet1.write(row, 12, '', style_header2)

                row = 17
                sheet1.merge_range(row, 0, row, 1, '')
                sheet1.merge_range(row, 2, row, 12,
                                   '(*) = Overtime &  Expenses reimbursable ONLY if previously authorized by Applus Italy s.r.l.')

                row = 19
                sheet1.merge_range(row, 0, row, 5, '')
                sheet1.merge_range(row, 6, row, 12, '%  Working time divided per P.O. ', style_header2)

                row = 20
                sheet1.merge_range(row, 0, row, 5, '')
                sheet1.write(row, 6, 'Mon', style_header2)
                sheet1.write(row, 7, 'Tue', style_header2)
                sheet1.write(row, 8, 'Wed', style_header2)
                sheet1.write(row, 9, 'Thu', style_header2)
                sheet1.write(row, 10, 'Fri', style_header2)
                sheet1.write(row, 11, 'Sat', style_header2)
                sheet1.write(row, 12, 'Sun', style_header2)

                row = 21
                sheet1.write(row, 0, 'JA', style_header2)
                sheet1.write(row, 1, 'PSC-Job', style_header2)
                sheet1.write(row, 2, 'PO', style_header2)
                sheet1.write(row, 3, 'Report No', style_header2)
                sheet1.write(row, 4, 'Vendor', style_header2)
                sheet1.write(row, 5, 'Location', style_header2)
                end_row = row
                row1 = row
                totol_fullday += 1

                unique = ''
                uni = []
                for col in range(6, 13):
                    sheet1.write(9, col, '', style_header2)
                    sheet1.write(10, col, '', style_header2)
                    sheet1.write(11, col, '', style_header2)
                    sheet1.write(21, col, '', style_header2)
                    sheet1.write(22, col, '', style_header2)
                    sheet1.write(24, col, '', style_header2)
                for val in records:
                    un = val['unique_no']
                    txn = val['txn']
                    part = str(un) if un else str(txn)
                    if part not in uni:
                        uni.append(part)
                        unique += str(part) + '_'
                    calendar_startt_day = datetime.strptime(str(val['start']), "%d-%m-%Y").strftime("%A")

                    if calendar_startt_day == 'Monday':
                        sheet1.write(21, 6, val['start'], style_header2)

                    if calendar_startt_day == 'Tuesday':
                        sheet1.write(21, 7, val['start'], style_header2)

                    if calendar_startt_day == 'Wednesday':
                        sheet1.write(21, 8, val['start'], style_header2)

                    if calendar_startt_day == 'Thursday':
                        sheet1.write(21, 9, val['start'], style_header2)

                    if calendar_startt_day == 'Friday':
                        sheet1.write(21, 10, val['start'], style_header2)

                    if calendar_startt_day == 'Saturday':
                        sheet1.write(21, 11, val['start'], style_header2)

                    if calendar_startt_day == 'Sunday':
                        sheet1.write(21, 12, val['start'], style_header2)


                    row = 22
                    row1 += 1
                    sheet1.write(row, 0, val['job_assign'], style_center_align)
                    sheet1.write(row, 1, val['pscjob'], style_center_align)
                    sheet1.write(row, 2, val['purchase'], style_center_align)
                    sheet1.write(row, 3, val['number'], style_center_align_wrap)
                    sheet1.write(row, 4, val['vendor'], style_center_align_wrap)
                    sheet1.write(row, 5, val['v_location'], style_center_align_wrap)
                    if calendar_startt_day == 'Monday':
                        if val['allday']:
                            sheet1.write(row, 6, '100%', style_header2)
                            sheet1.write(24, 6, '100%', style_header2)
                        else:
                            sheet1.write(row, 6, '50%', style_header2)
                            sheet1.write(24, 6, '50%', style_header2)

                    if calendar_startt_day == 'Tuesday':
                        if val['allday']:
                            sheet1.write(row, 7, '100%', style_header2)
                            sheet1.write(24, 7, '100%', style_header2)
                        else:
                            sheet1.write(row, 7, '50%', style_header2)
                            sheet1.write(24, 7, '50%', style_header2)

                    if calendar_startt_day == 'Wednesday':
                        if val['allday']:
                            sheet1.write(row, 8, '100%', style_header2)
                            sheet1.write(24, 8, '100%', style_header2)
                        else:
                            sheet1.write(row, 8, '50%', style_header2)
                            sheet1.write(24, 8, '50%', style_header2)

                    if calendar_startt_day == 'Thursday':
                        if val['allday']:
                            sheet1.write(row, 9, '100%', style_header2)
                            sheet1.write(24, 9, '100%', style_header2)
                        else:
                            sheet1.write(row, 9, '50%', style_header2)
                            sheet1.write(24, 9, '50%', style_header2)

                    if calendar_startt_day == 'Friday':
                        if val['allday']:
                            sheet1.write(row, 10, '100%', style_header2)
                            sheet1.write(24, 10, '100%', style_header2)
                        else:
                            sheet1.write(row, 10, '50%', style_header2)
                            sheet1.write(24, 10, '50%', style_header2)

                    if calendar_startt_day == 'Saturday':
                        if val['allday']:
                            sheet1.write(row, 11, '100%', style_header2)
                            sheet1.write(24, 11, '100%', style_header2)
                        else:
                            sheet1.write(row, 11, '50%', style_header2)
                            sheet1.write(24, 11, '50%', style_header2)

                    if calendar_startt_day == 'Sunday':
                        if val['allday']:
                            sheet1.write(row, 12, '100%', style_header2)
                            sheet1.write(24, 12, '100%', style_header2)
                        else:
                            sheet1.write(row, 12, '50%', style_header2)
                            sheet1.write(24, 12, '50%', style_header2)


                    if calendar_startt_day == 'Monday':
                        sheet1.write(9, 6, val['start'], style_header2)

                    if calendar_startt_day == 'Tuesday':
                        sheet1.write(9, 7, val['start'], style_header2)

                    if calendar_startt_day == 'Wednesday':
                        sheet1.write(9, 8, val['start'], style_header2)

                    if calendar_startt_day == 'Thursday':
                        sheet1.write(9, 9, val['start'], style_header2)

                    if calendar_startt_day == 'Friday':
                        sheet1.write(9, 10, val['start'], style_header2)

                    if calendar_startt_day == 'Saturday':
                        sheet1.write(9, 11, val['start'], style_header2)

                    if calendar_startt_day == 'Sunday':
                        sheet1.write(9, 12, val['start'], style_header2)


                    if calendar_startt_day == 'Monday':
                        if val['allday']:
                            sheet1.write(10, 6, 'F', style_header2)
                        else:
                            sheet1.write(10, 6, 'H', style_header2)

                    if calendar_startt_day == 'Tuesday':
                        if val['allday']:
                            sheet1.write(10, 7, 'F', style_header2)
                        else:
                            sheet1.write(10, 7, 'H', style_header2)

                    if calendar_startt_day == 'Wednesday':
                        if val['allday']:
                            sheet1.write(10, 8, 'F', style_header2)
                        else:
                            sheet1.write(10, 8, 'H', style_header2)

                    if calendar_startt_day == 'Thursday':
                        if val['allday']:
                            sheet1.write(10, 9, 'F', style_header2)
                        else:
                            sheet1.write(10, 9, 'H', style_header2)

                    if calendar_startt_day == 'Friday':
                        if val['allday']:
                            sheet1.write(10, 10, 'F', style_header2)
                        else:
                            sheet1.write(10, 10, 'H', style_header2)

                    if calendar_startt_day == 'Saturday':
                        if val['allday']:
                            sheet1.write(10, 11, 'F', style_header2)
                        else:
                            sheet1.write(10, 11, 'H', style_header2)

                    if calendar_startt_day == 'Sunday':
                        if val['allday']:
                            sheet1.write(10, 12, 'F', style_header2)
                        else:
                            sheet1.write(10, 12, 'H', style_header2)


                    if calendar_startt_day == 'Monday':
                        sheet1.write(11, 6, val['kms_new'], style_header2)

                    if calendar_startt_day == 'Tuesday':
                        sheet1.write(11, 7, val['kms_new'], style_header2)

                    if calendar_startt_day == 'Wednesday':
                        sheet1.write(11, 8, val['kms_new'], style_header2)

                    if calendar_startt_day == 'Thursday':
                        sheet1.write(11, 9, val['kms_new'], style_header2)

                    if calendar_startt_day == 'Friday':
                        sheet1.write(11, 10, val['kms_new'], style_header2)

                    if calendar_startt_day == 'Saturday':
                        sheet1.write(11, 11, val['kms_new'], style_header2)

                    if calendar_startt_day == 'Sunday':
                        sheet1.write(11, 12, val['kms_new'], style_header2)



                sheet1.merge_range(24, 0, 24, 5, 'TOTAL', style_header)

                sheet1.merge_range(26, 0, 26, 12, 'NOTES', style_header)

                sheet1.set_row(27, 100)
                sheet1.merge_range(27, 0, 27, 12, '', style_header)


                sheet1.merge_range(28, 0, 28, 12,
                                   'L5-ITA-FMT-257 (rev0)_Sample daily T&E_blank_12/02/2020')

                row = 10
                sheet1.merge_range(row, 0, row, 1, '')
                sheet1.merge_range(row, 2, row, 4, 'F= Full Day - H= Half Day', style_header2)
                sheet1.write(row, 5, '', style_header2)

                row = 11
                sheet1.merge_range(row, 0, row, 1, '')
                sheet1.merge_range(row, 2, row, 4, 'Km', style_header2)
                sheet1.write(row, 5, '', style_header2)

                workbook.close()
                out = base64.encodebytes(output.getvalue())
                data.append(('%s_%s_%s.xlsx' % (unique, start, category), out))

        self._create_zip_from_xlsx_data(data)

        report_common_method.send_report_notification(
            self.env,
            self.file_name,
            self.file,
            'applus.summary.report',
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
            'views': [(self.env.ref('petrofac_report.applus_summary_report_view').id, 'form')],
            'res_model': 'applus.summary.report',
            'target': 'new',
            'context': self._context
        }
