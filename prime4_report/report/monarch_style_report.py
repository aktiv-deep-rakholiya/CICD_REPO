from odoo import models, fields, api, _
import base64
from io import BytesIO
import xlsxwriter
from odoo.exceptions import UserError
from odoo.tools.misc import file_path as get_file_path
from odoo.addons.project_management import report_common_method


class MonarchStyleReport(models.TransientModel):
    _name = 'monarch.style.report'
    _inherit = 'common.report'
    _description = 'Monarch Style Report'

    def generate_report_excel(self):

        domain, fromdate, todate = self._get_calendar_domain(
            client_code='monarch',
            include_status=False,
            extra_domain=[]
        )

        calendar_event = self.env['calendar.event'].search(domain, order="start")
        if not calendar_event:
            raise UserError(_("No Record Found"))

        def monarch_value_builder(record):
            values = self._build_common_values(record)

            hrs_new = record.hrs or 0
            travl_hrs = record.travel_hrs or 0
            report_hrs = record.report_hrs or 0

            values.update({
                'extra_hrs_new': record.extra_hrs or 0,
                'hrs_new': hrs_new,
                'travl_hrs': travl_hrs,
                'report_hrs': report_hrs,
                'total_hrs_all': hrs_new + travl_hrs + report_hrs,
                'kms_new': record.add_km_mileage1 or 0,
                'extra_kms_new': record.extra_kms or 0,
                'note_new': record.note or '',
            })

            return values

        start_values_data = self._group_calendar_records(
            calendar_event, monarch_value_builder
        )

        total_hrs = 0
        totol_fullday = 0
        totol_halfday = '-'
        start_values_data_sort = sorted(start_values_data.items())
        data = []
        for start, categorious in start_values_data_sort:
            for category, records in categorious.items():
                byte_io = BytesIO()
                workbook = xlsxwriter.Workbook(byte_io)
                sheet1 = workbook.add_worksheet(category)
                style_header_new_no_line = workbook.add_format({'bold': True, 'font_size': 8, 'font_name': 'Arial',
                                                                'align': 'left', 'valign': 'vcenter', 'text_wrap': True})

                style_header_new_with_line = workbook.add_format({'bold': True, 'font_size': 11, 'font_name': 'Calibri',
                                                                  'align': 'center', 'valign': 'vcenter',
                                                                  'text_wrap': True,
                                                                  'right': 1, 'top': 1, 'left': 1, 'bottom': 1, })

                style_header_new_with_line_align_left = workbook.add_format(
                    {'bold': True, 'font_size': 11, 'font_name': 'Calibri',
                     'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'right': 1, 'top': 1, 'left': 1,
                     'bottom': 1, })

                style_header_new_with_line_size_18 = workbook.add_format(
                    {'bold': True, 'font_size': 18, 'font_name': 'Calibri',
                     'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'right': 1, 'top': 1, 'left': 1,
                     'bottom': 1, })

                style_header_new_with_line_size_24 = workbook.add_format(
                    {'bold': True, 'font_size': 24, 'font_name': 'Times New Roman',
                     'align': 'left', 'valign': 'vcenter', 'italic': True, 'text_wrap': True, 'right': 1, 'top': 1,
                     'left': 1,
                     'bottom': 1, 'font_color': '#6666FF'})

                style_center_align = workbook.add_format({'bold': False, 'font_size': 11, 'font_name': 'Arial',
                                                          'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                                                          'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_center_align_color = workbook.add_format({'bold': False, 'font_size': 11, 'font_name': 'Arial',
                                                                'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                                                                'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_center_align_wrap = workbook.add_format({'bold': False, 'font_size': 11, 'font_name': 'Arial',
                                                               'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                                                               'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_center_align_wrap_color = workbook.add_format(
                    {'bold': False, 'font_size': 11, 'font_name': 'Arial',
                     'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                sheet1.set_column(0, 0, 9.00)
                sheet1.set_column(1, 1, 19.00)
                sheet1.set_column(2, 2, 11.00)
                sheet1.set_column(3, 3, 20.00)
                sheet1.set_column(4, 4, 21.00)
                sheet1.set_column(5, 5, 10.00)
                sheet1.set_column(6, 6, 7.00)
                sheet1.set_column(7, 7, 11.00)
                sheet1.set_column(8, 8, 7.00)
                sheet1.set_column(9, 9, 8.50)
                sheet1.set_column(10, 15, 6.00)
                sheet1.set_column(15, 15, 11.00)

                sheet1.set_row(0, 30)

                sheet1.fit_to_pages(1, 0)
                sheet1.set_landscape()
                sheet1.header_str = ''
                sheet1.footer_str = ''
                sheet1.set_row(0, 70)

                image_path = get_file_path('prime4_report/static/src/img/logo.jpg')
                with open(image_path, 'rb') as f:
                    img_bytes = BytesIO(f.read())

                img_bytes.seek(0)

                sheet1.set_row(0, 75)
                sheet1.insert_image(0, 0, 'logo.jpg', {
                    'image_data': img_bytes,
                    'x_scale': 0.6,
                    'y_scale': 0.6,
                    'x_offset': 0,
                    'y_offset': 0,
                })
                row = 1

                sheet1.merge_range(row, 1, row + 4, 3, '', style_header_new_no_line)

                sheet1.merge_range(row, 4, row + 4, 9, 'Presenze giornaliere \nTime Sheet',
                                   style_header_new_with_line_size_18)
                sheet1.merge_range(row, 10, row, 15, 'No.', style_header_new_with_line_size_24)
                sheet1.merge_range(row + 1, 10, row + 4, 15, 'Date:', style_header_new_with_line_size_24)

                row = 6
                sheet1.merge_range(row, 0, row, 12, '', style_header_new_no_line)

                row = 9

                sheet1.write(row, 1, 'FORNITORE \nSUPPLIER', style_header_new_with_line)
                sheet1.write(row, 2, 'DATA \nDATE', style_header_new_with_line)
                sheet1.write(row, 3, 'Project N°', style_header_new_with_line)
                sheet1.write(row, 4, 'Commessa Cliente N°\n CLIENT JOB N°', style_header_new_with_line)
                sheet1.merge_range(row, 5, row, 6, 'LOCALITA’\nLOCATION', style_header_new_with_line)
                sheet1.write(row, 7, 'Attività \nActivity', style_header_new_with_line)
                sheet1.write(row, 8, 'h Viaggio\nTravel', style_header_new_with_line)
                sheet1.write(row, 9, 'h Presenza\npresence', style_header_new_with_line)
                sheet1.write(row, 10, 'h Report', style_header_new_with_line)
                sheet1.write(row, 11, 'h Tot. ', style_header_new_with_line)
                sheet1.write(row, 12, 'Over\nTime', style_header_new_with_line)
                sheet1.write(row, 13, 'Km', style_header_new_with_line)
                sheet1.write(row, 14, 'Over\nKm', style_header_new_with_line)
                sheet1.write(row, 15, 'Note', style_header_new_with_line)

                end_row = row
                row1 = row
                totol_fullday += 1

                location_name = calendar_event[0].v_location.name if calendar_event[0].v_location.id != False else ''
                unique = ''
                uni = []
                for val in records:
                    un = val['unique_no']
                    txn = val['txn']
                    part = str(un) if un else str(txn)
                    if part not in uni:
                        uni.append(part)
                        unique += str(part) + '_'
                    row += 1
                    row1 += 1
                    sheet1.write(row, 1, self.vendor_id.name, style_center_align)
                    sheet1.write(row, 2, val['start'], style_center_align)
                    sheet1.write(row, 3, self.project_id.name, style_center_align)
                    sheet1.write(row, 4, val['purchase'], style_center_align_wrap)
                    sheet1.merge_range(row, 5, row, 6, location_name, style_center_align_wrap_color)
                    sheet1.write(row, 7, val['employee_role'], style_center_align_wrap)

                    if val['allday']:
                        sheet1.write(row, 8, val['travl_hrs'], style_center_align_wrap)
                        sheet1.write(row, 9, val['hrs_new'], style_center_align_wrap)
                        sheet1.write(row, 10, val['report_hrs'], style_center_align_wrap)
                        total_hrs += val['total_hrs_all']

                    sheet1.write(row, 11, val['total_hrs_all'], style_center_align)
                    sheet1.write(row, 12, val['extra_hrs_new'], style_center_align)
                    sheet1.write(row, 13, val['kms_new'], style_center_align)
                    sheet1.write(row, 14, val['extra_kms_new'], style_center_align_color)
                    sheet1.write(row, 15, val['note_new'], style_center_align_color)

                    end_row = row1

                row = 6
                if calendar_event[0]:
                    if calendar_event[0].start:
                        calendar_start_date = calendar_event[0].start.strftime("%b-%Y")
                    else:
                        calendar_start_date = ''
                sheet1.merge_range(row, 1, row, 4, 'ISPETTORE/INSPECTOR: ' + str(start.split('_')[-1]),
                                   style_header_new_with_line_align_left)
                sheet1.merge_range(row, 5, row, 9, 'CLIENTE/CLIENT: MONARCH STYLE',
                                   style_header_new_with_line_align_left)
                sheet1.merge_range(row, 10, row, 15, 'MESE DI/MONTH of : ' + calendar_start_date,
                                   style_header_new_with_line_align_left)

                workbook.close()
                file_data = byte_io.getvalue()
                file_content = base64.b64encode(file_data)
                data.append(('%s_%s_%s.xlsx' % (unique, start, category), file_content))

        self._create_zip_from_xlsx_data(data)

        report_common_method.send_report_notification(
            self.env,
            self.file_name,
            self.file,
            'monarch.style.report',
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
            'res_model': 'monarch.style.report',
            'target': 'new',
            'context': self._context
        }
