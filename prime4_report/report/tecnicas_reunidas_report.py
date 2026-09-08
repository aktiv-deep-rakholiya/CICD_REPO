from odoo import models, fields, api, _
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools.misc import file_path as get_file_path
from odoo.addons.project_management import report_common_method


class TecnicasSummaryReport(models.TransientModel):
    _name = 'tecnicas.reunidas.summary.report'
    _inherit = 'common.report'
    _description = 'Tecnicas Reunidas Report'

    agency_idd = fields.Many2one('agency.number', string='Agency')

    def generate_report_excel(self):

        domain, fromdate, todate = self._get_calendar_domain(
            client_code='',
            include_status=False,
            extra_domain=[
                ('agency_id_name', '=', self.agency_idd.id) if self.agency_idd else (),
            ]
        )

        calendar_event = self.env['calendar.event'].search(domain, order="start")
        if not calendar_event:
            raise UserError(_("No Record Found"))

        def tecnicas_value_builder(record):
            values = self._build_common_values(record)
            hrs_new = record.hrs
            travl_hrs = record.travel_hrs
            report_hrs = record.report_hrs
            total_hrs_all = hrs_new + travl_hrs + report_hrs
            hotel = record.add_expenses_rtpcr1 or 0
            travel = record.add_expenses_airfare1 or 0
            total_expenses = travel + hotel
            values.update({
                'hrs_new': hrs_new,
                'travl_hrs': travl_hrs,
                'report_hrs': report_hrs,
                'total_hrs_all': total_hrs_all,
                'kms_new': record.add_km_mileage1 or 0,
                'hotel': hotel,
                'travel': travel,
                'total_expenses': total_expenses,
            })

            return values

        start_values_data = self._group_calendar_records(
            calendar_event, tecnicas_value_builder
        )

        total_hrs = 0
        totol_fullday = 0
        totol_halfday = '-'
        start_values_data_sort = sorted(start_values_data.items())
        data = []
        for start, categorious in start_values_data_sort:
            for category, records in categorious.items():
                uni = []
                byte_io = BytesIO()
                workbook = xlsxwriter.Workbook(byte_io)
                sheet1 = workbook.add_worksheet(category)


                style_header = workbook.add_format(
                    {'bold': True, 'font_size': 8, 'font_name': 'Arial', 'text_wrap': 1, 'align': 'center',
                     'valign': 'vcenter', 'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_header1 = workbook.add_format(
                    {'bold': True, 'underline': True, 'font_size': 14, 'font_name': 'Arial', 'text_wrap': 1,
                     'align': 'center',
                     'valign': 'vcenter'})

                style_header_left = workbook.add_format({'bold': True, 'font_size': 10, 'font_name': 'Arial',
                                                         'text_wrap': 1, 'align': 'left', 'valign': 'vcenter',
                                                         'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_header_left_no_bold = workbook.add_format({'bold': False, 'font_size': 10, 'font_name': 'Arial',
                                                                 'text_wrap': 1, 'align': 'center', 'valign': 'vcenter',
                                                                 'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_header_left_no_bold_left = workbook.add_format(
                    {'bold': False, 'font_size': 10, 'font_name': 'Arial',
                     'text_wrap': 1, 'align': 'left', 'valign': 'vcenter', 'right': 1, 'left': 1, 'top': 1,
                     'bottom': 1})

                style_header_left_align_right = workbook.add_format(
                    {'bold': True, 'font_size': 10, 'font_name': 'Arial',
                     'align': 'right', 'valign': 'vcenter', 'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_header_no_border_align_right = workbook.add_format(
                    {'bold': True, 'font_size': 10, 'font_name': 'Arial',
                     'align': 'right', 'valign': 'vcenter'})

                style_header_left_border_align_right = workbook.add_format(
                    {'bold': True, 'font_size': 10, 'font_name': 'Arial',
                     'align': 'right', 'valign': 'vcenter', 'left': 1})

                style_header_right_border_align_right = workbook.add_format(
                    {'bold': True, 'font_size': 10, 'font_name': 'Arial',
                     'align': 'left', 'valign': 'vcenter', 'right': 1})

                style_header_right_bot_border_align_right = workbook.add_format(
                    {'bold': True, 'font_size': 10, 'font_name': 'Arial',
                     'align': 'left', 'valign': 'vcenter', 'right': 1, 'bottom': 1})

                style_header_left_bot_border_align_right = workbook.add_format(
                    {'bold': True, 'font_size': 10, 'font_name': 'Arial',
                     'align': 'left', 'valign': 'vcenter', 'left': 1, 'bottom': 1})

                style_header_right_top_border_align_right = workbook.add_format(
                    {'bold': True, 'font_size': 12, 'font_name': 'Arial',
                     'align': 'center', 'valign': 'vcenter', 'right': 1, 'top': 1})

                style_header_right_top_left_border_align_right = workbook.add_format(
                    {'bold': True, 'font_size': 12, 'font_name': 'Arial',
                     'align': 'right', 'valign': 'vcenter', 'right': 1, 'top': 1, 'left': 1})

                style_header_new_no_line = workbook.add_format({'bold': True, 'font_size': 8, 'font_name': 'Arial',
                                                                'align': 'left', 'valign': 'vcenter', 'text_wrap': 1})

                style_header2 = workbook.add_format(
                    {'bold': True, 'italic': True, 'font_size': 11, 'font_name': 'Arial',
                     'align': 'center', 'valign': 'vcenter', 'right': 1, 'top': 1, 'left': 1, 'bottom': 1,
                     'text_wrap': 1})

                style_header_left_color_14 = workbook.add_format({'bold': True, 'font_size': 14, 'font_name': 'Arial',
                                                                  'align': 'center', 'valign': 'vcenter', 'right': 1,
                                                                  'top': 1, 'left': 1, 'bottom': 1, 'text_wrap': 1,
                                                                  'bg_color': '#CCCCFF'})

                style_header2_color_14 = workbook.add_format({'bold': True, 'font_size': 14, 'font_name': 'Arial',
                                                              'align': 'center', 'valign': 'vcenter', 'right': 1,
                                                              'top': 1, 'left': 1, 'bottom': 1, 'text_wrap': 1,
                                                              'bg_color': '#CCCCFF'})

                style_header_right_14 = workbook.add_format({'bold': True, 'font_size': 14, 'font_name': 'Arial',
                                                             'align': 'right', 'valign': 'vcenter', 'text_wrap': 1})

                style_center_align = workbook.add_format({'bold': False, 'font_size': 11, 'font_name': 'Arial',
                                                          'align': 'center', 'valign': 'vcenter', 'text_wrap': 1,
                                                          'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_center_align_color = workbook.add_format({'bold': False, 'font_size': 11, 'font_name': 'Arial',
                                                                'align': 'center', 'valign': 'vcenter', 'text_wrap': 1,
                                                                'right': 1, 'left': 1, 'top': 1, 'bottom': 1,
                                                                'bg_color': '#CCCCFF'})

                style_left_align = workbook.add_format({'bold': False, 'font_size': 11, 'font_name': 'Arial',
                                                        'align': 'left', 'valign': 'vcenter', 'text_wrap': 1,
                                                        'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_header_center = workbook.add_format(
                    {'bold': True, 'italic': True, 'font_size': 11, 'font_name': 'Arial',
                     'align': 'center', 'valign': 'vcenter', 'text_wrap': 1, 'right': 1, 'left': 1, 'top': 1,
                     'bottom': 1})

                style_header_right = workbook.add_format({'bold': True, 'font_size': 12, 'font_name': 'Arial',
                                                          'align': 'right', 'valign': 'vcenter', 'text_wrap': 1})

                style_center_align_wrap = workbook.add_format({'bold': False, 'font_size': 11, 'font_name': 'Arial',
                                                               'align': 'center', 'valign': 'vcenter', 'text_wrap': 1,
                                                               'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_center_align_wrap_color = workbook.add_format(
                    {'bold': False, 'font_size': 11, 'font_name': 'Arial',
                     'align': 'center', 'valign': 'vcenter', 'text_wrap': 1, 'right': 1, 'left': 1, 'top': 1,
                     'bottom': 1, 'bg_color': '#CCCCFF'})

                sheet1.set_column(0, 0, 14.00)
                sheet1.set_column(1, 1, 10.00)
                sheet1.set_column(2, 2, 10.00)
                sheet1.set_column(3, 3, 15.00)
                sheet1.set_column(4, 4, 15.00)
                sheet1.set_column(5, 5, 10.00)
                sheet1.set_column(6, 6, 13.00)
                sheet1.set_column(7, 7, 15.00)
                sheet1.set_column(8, 8, 10.00)
                sheet1.set_column(9, 9, 17.00)
                sheet1.set_column(10, 10, 17.00)
                sheet1.set_column(11, 11, 17.00)
                sheet1.set_column(12, 12, 17.00)

                sheet1.fit_to_pages(1, 0)
                sheet1.set_landscape()
                sheet1.header_str = ''
                sheet1.footer_str = ''
                image_path = get_file_path('prime4_report/static/src/img/logo.jpg')
                with open(image_path, 'rb') as f:
                    img_bytes = BytesIO(f.read())

                img_bytes.seek(0)
                sheet1.set_row(0, 70)
                sheet1.insert_image(0, 0, 'logo.jpg', {
                    'image_data': img_bytes,
                    'x_scale': 0.6,
                    'y_scale': 0.6,
                    'x_offset': 0,
                    'y_offset': 0,
                })
                row = 0
                row = 1
                sheet1.merge_range(row, 0, row, 12, '', style_header_new_no_line)
                row = 2
                sheet1.merge_range(row, 0, row, 12, '', style_header_new_no_line)
                # row = 3
                # sheet1.merge_range(row, row, 0, 12, '', style_header_new_no_line)
                row = 4
                sheet1.merge_range(row, 0, row, 12, '', style_header_new_no_line)
                row = 5
                sheet1.merge_range(row, 0, row, 12, '', style_header_new_no_line)
                row += 8

                sheet1.merge_range(row, 0, row + 1, 0, 'Date', style_header2)
                sheet1.merge_range(row, 1, row, 4, 'Hours', style_header2)

                sheet1.merge_range(row, 5, row + 1, 5, 'Km', style_header2)
                sheet1.merge_range(row, 6, row + 1, 6, 'Tolls', style_header2)
                sheet1.merge_range(row, 7, row + 1, 7, 'Air/Train Ticket', style_header2)
                sheet1.merge_range(row, 8, row + 1, 8, 'Hotel', style_header2)
                sheet1.merge_range(row, 9, row + 1, 9, 'Diner', style_header2)
                sheet1.merge_range(row, 10, row, 11, 'Other Expenses', style_header2)
                sheet1.merge_range(row, 12, row + 1, 12, 'Total', style_header2)

                row += 1
                sheet1.write(row, 1, 'Visit', style_header2)
                sheet1.write(row, 2, 'Report', style_header2)
                sheet1.write(row, 3, 'Travel', style_header2)
                sheet1.write(row, 4, 'Total', style_header2)
                sheet1.write(row, 10, 'Description', style_header2)
                sheet1.write(row, 11, 'Quantity', style_header2)
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
                        unique += part + '_'
                    row += 1
                    row1 += 1
                    sheet1.write(row, 0, val['start'], style_center_align)
                    if val['allday']:
                        sheet1.write(row, 1, val['hrs_new'], style_center_align_wrap)
                        sheet1.write(row, 2, val['report_hrs'], style_center_align_wrap)
                        sheet1.write(row, 3, val['travl_hrs'], style_center_align_wrap)
                        sheet1.write(row, 4, val['total_hrs_all'], style_center_align_wrap_color)
                        total_hrs += val['total_hrs_all']

                    sheet1.write(row, 5, val['kms_new'], style_center_align)
                    sheet1.write(row, 6, '', style_center_align)
                    sheet1.write(row, 7, val['travel'], style_center_align)
                    sheet1.write(row, 8, val['hotel'], style_center_align)
                    sheet1.write(row, 9, '', style_center_align)
                    sheet1.write(row, 10, '', style_center_align)
                    sheet1.write(row, 11, '', style_center_align)
                    sheet1.write(row, 12, val['total_expenses'], style_center_align_color)
                    expense = val

                    end_row = row1

                next_row1 = end_row + 1
                sheet1.write(next_row1, 0, '', style_header)
                sheet1.write(next_row1, 1, '', style_header)
                sheet1.write(next_row1, 2, '', style_header)
                sheet1.write(next_row1, 3, '', style_header)
                sheet1.write(next_row1, 4, '', style_header)
                sheet1.write(next_row1, 5, '', style_left_align)

                sheet1.write(next_row1, 6, '', style_center_align)
                sheet1.write(next_row1, 7, '', style_center_align)
                sheet1.write(next_row1, 8, '', style_center_align)
                sheet1.write(next_row1, 9, '', style_center_align)
                sheet1.write(next_row1, 10, '', style_center_align)
                sheet1.write(next_row1, 11, '', style_center_align)
                sheet1.write(next_row1, 12, '', style_center_align)

                next_row = next_row1 + 1
                sheet1.merge_range(next_row, 0, next_row, 1, 'Reason For Extra Hours:', style_header_left_no_bold_left)
                sheet1.merge_range(next_row, 2, next_row, 12, '', style_header_left)

                formula_total = 'SUM' + '(' + 'E16' + ':' + 'E' + str(next_row1) + ')'
                formula_expense = 'SUM' + '(' + 'M16' + ':' + 'M' + str(next_row1) + ')'

                next1_row = next_row + 1
                sheet1.merge_range(next1_row, 0, next1_row, 3, 'Total Hours :', style_header_right_14)
                sheet1.write_formula(next1_row, 4, formula_total, style_header2_color_14)
                # sheet1.write(next1_row, 4,str(total_hrs), style_header2)
                sheet1.merge_range(next1_row, 5, next1_row, 9, '', style_header_right)
                sheet1.merge_range(next1_row, 10, next1_row, 11, 'TOTAL EXPENSES :', style_header_right_14)
                sheet1.write_formula(next1_row, 12, formula_expense, style_header_left_color_14)

                next6_row = next1_row + 2
                sheet1.merge_range(next6_row, 0, next6_row, 4, 'Inspector', style_header_right_top_border_align_right)
                sheet1.write(next6_row, 5, start.split('_')[-1], style_header_right)
                sheet1.merge_range(next6_row, 6, next6_row, 7, 'Inspection Coordinator : ',
                                   style_header_right_top_left_border_align_right)
                sheet1.merge_range(next6_row, 8, next6_row, 11, self.env.user.name, style_header_left)

                next33_row = next6_row + 1
                sheet1.write(next33_row, 0, '', style_header_no_border_align_right)
                sheet1.merge_range(next33_row, 1, next33_row, 4, '', style_header_right_border_align_right)

                sheet1.write(next33_row, 5, '', style_header_right)
                sheet1.write(next33_row, 6, 'Checked Up:', style_header_left_border_align_right)
                sheet1.merge_range(next33_row, 7, next33_row, 11, self.env.user.name,
                                   style_header_right_border_align_right)

                next34_row = next33_row + 1
                sheet1.write(next34_row, 0, '', style_header_no_border_align_right)
                sheet1.write(next34_row, 5, '', style_header_right)
                sheet1.write(next34_row, 6, '', style_header_left_border_align_right)

                next35_row = next34_row + 1
                sheet1.write(next35_row, 0, '', style_header_no_border_align_right)
                sheet1.write(next35_row, 5, '', style_header_right)
                sheet1.write(next35_row, 6, '', style_header_left_border_align_right)

                next36_row = next35_row + 1
                sheet1.write(next36_row, 0, 'Signature:', style_header_no_border_align_right)
                sheet1.write(next36_row, 5, '', style_header_right)
                sheet1.write(next36_row, 6, 'Signature:', style_header_left_border_align_right)

                next37_row = next36_row + 1
                sheet1.write(next37_row, 0, '', style_header_no_border_align_right)
                sheet1.write(next37_row, 5, '', style_header_right)
                sheet1.write(next37_row, 6, '', style_header_left_border_align_right)

                next38_row = next37_row + 1
                sheet1.write(next38_row, 0, '', style_header_no_border_align_right)
                sheet1.merge_range(next34_row, 1, next38_row, 4, '', style_header_right_border_align_right)
                sheet1.write(next38_row, 5, '', style_header_right)
                sheet1.write(next38_row, 6, '', style_header_left_border_align_right)
                sheet1.merge_range(next34_row, 7, next38_row, 11, '', style_header_right_border_align_right)

                next39_row = next38_row + 1
                sheet1.write(next39_row, 0, 'Date:', style_header_no_border_align_right)
                sheet1.merge_range(next39_row, 1, next39_row, 4, datetime.today().strftime('%d-%m-%Y'),
                                   style_header_right_border_align_right)
                sheet1.write(next39_row, 5, '', style_header_right)
                sheet1.write(next39_row, 6, 'Date:', style_header_left_border_align_right)
                sheet1.merge_range(next39_row, 7, next39_row, 11, '', style_header_right_border_align_right)

                next3_row = next39_row + 1
                sheet1.merge_range(next3_row, 0, next3_row, 4, '', style_header_right_bot_border_align_right)
                sheet1.write(next3_row, 5, '', style_header_right)
                sheet1.write(next3_row, 6, '', style_header_left_bot_border_align_right)
                sheet1.merge_range(next3_row, 7, next3_row, 11, '', style_header_right_bot_border_align_right)

                row = 12

                sheet1.merge_range(row, 0, row, 5, '', style_header_right)
                sheet1.merge_range(row, 6, row, 12, 'Expenses', style_header_center)

                row = 10

                sheet1.merge_range(row, 0, row, 2, 'Travel Location :', style_header_right)
                sheet1.write(row, 3, 'From :', style_header_left_align_right)
                sheet1.merge_range(row, 4, row, 6, '', style_header_left)
                sheet1.write(row, 7, 'To :', style_header_left_align_right)
                sheet1.merge_range(row, 8, row, 10, '', style_header_left)

                row = 8

                if len(po_value) > 0:
                    po_numbers = ','.join(po_value)
                else:
                    po_numbers = ''

                if (len(po_numbers) + 25) > 36:
                    height_factor = int((len(po_numbers) + 25) / 36) + 1

                location_name = calendar_event[0].v_location.name if calendar_event[0].v_location.id != False else ''
                sheet1.merge_range(row, 0, row, 2, 'TR PO Number/Reference :', style_header_right)
                sheet1.merge_range(row, 3, row, 4, po_numbers, style_header_left_no_bold)
                sheet1.write(row, 5, '', style_header_right)
                sheet1.merge_range(row, 6, row, 7, 'Vendor/Subvendor : ', style_header_right)
                sheet1.merge_range(row, 8, row, 9, val['vendor'], style_header_left_no_bold)
                sheet1.merge_range(row, 10, row, 11, 'Inspection Location : ', style_header_right)
                sheet1.write(row, 12, location_name, style_header_left_no_bold)

                row = 6
                sheet1.merge_range(row, 0, row, 2, 'Agency :', style_header_right)
                sheet1.merge_range(row, 3, row, 4, self.agency_idd.name, style_header_left_no_bold)
                sheet1.merge_range(row, 6, row, 7, 'Inspector/Expeditor :', style_header_right)

                sheet1.merge_range(row, 8, row, 9, self.inspector_id.ins_name, style_header_left_no_bold)

                row = 3
                if calendar_event[0]:
                    if calendar_event[0].start:

                        calendar_start_date = calendar_event[0].start.strftime("%b-%Y")
                    else:
                        calendar_start_date = ''
                    sheet1.merge_range(row, 0, row, 12, 'Time & Expenses Sheet', style_header1)
                else:
                    sheet1.write(5, 5, '', style_header1)

                next5_row = next3_row + 2

                next6_row = next5_row + 4

                workbook.close()
                file_data = byte_io.getvalue()
                file_content = base64.b64encode(file_data)
                data.append(('%s_%s_%s.xlsx' % (unique, start, category), file_content))

        self._create_zip_from_xlsx_data(data)

        report_common_method.send_report_notification(
            self.env,
            self.file_name,
            self.file,
            'tecnicas.reunidas.summary.report',
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
            'views': [(self.env.ref('prime4_report.tecnicas_summary_report_view').id, 'form')],
            'res_model': 'tecnicas.reunidas.summary.report',
            'target': 'new',
            'context': self._context
        }
