from odoo import models, fields, api, _
import base64
from io import BytesIO
import xlsxwriter
from odoo.exceptions import UserError
from odoo.tools.misc import file_path as get_file_path
from odoo.addons.project_management import report_common_method


class NeilBarnettSummaryReport(models.TransientModel):
    _name = 'neil.barnett.summary.report'
    _inherit = 'common.report'
    _description = 'Neil Barnett Report'

    def generate_report_excel(self):

        domain, fromdate, todate = self._get_calendar_domain(
            client_code='neilbarnett',
            include_status=False,
            extra_domain=[]
        )

        calendar_event = self.env['calendar.event'].search(domain, order="start")
        if not calendar_event:
            raise UserError(_("No Record Found"))

        def neilbarnett_value_builder(record):
            values = self._build_common_values(record)

            hrs_new = record.hrs
            travl_hrs = record.travel_hrs
            report_hrs = record.report_hrs
            total_hrs_all = hrs_new + travl_hrs + report_hrs

            values.update({
                'miscexpen': record.misc_expen or "",
                'hrs_new': hrs_new,
                'travl_hrs': travl_hrs,
                'report_hrs': report_hrs,
                'total_hrs_all': total_hrs_all,
                'end_client': record.end_client.name,
            })

            return values

        start_values_data = self._group_calendar_records(
            calendar_event, neilbarnett_value_builder
        )

        total_hrs = 0
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

                style_header1 = workbook.add_format(
                    {'bold': True, 'font_size': 9, 'font_name': 'Times New Roman', 'text_wrap': 1, 'align': 'center',
                     'valign': 'vcenter', 'bottom': 1, 'font_color': '#FF0000'})

                style_header_left_no_bold = workbook.add_format(
                    {'bold': False, 'font_size': 10, 'font_name': 'Times New Roman',
                     'text_wrap': 1, 'align': 'center', 'valign': 'vcenter', 'right': 1, 'left': 1, 'top': 1,
                     'bottom': 1})

                style_header_left_no_bold_left = workbook.add_format(
                    {'bold': False, 'font_size': 10, 'font_name': 'Times New Roman',
                     'text_wrap': 1, 'align': 'left', 'valign': 'vcenter', 'right': 1, 'left': 1, 'top': 1,
                     'bottom': 1})

                style_header_new_no_line = workbook.add_format(
                    {'bold': True, 'font_size': 16, 'font_name': 'Times New Roman',
                     'align': 'left', 'valign': 'vcenter', 'text_wrap': 1, 'font_color': '#3339FF'})

                style_header2 = workbook.add_format({'bold': True, 'font_size': 10, 'font_name': 'Times New Roman',
                                                     'align': 'center', 'valign': 'vcenter', 'right': 1, 'top': 1,
                                                     'left': 1, 'bottom': 1, 'text_wrap': 1})

                style_center_align = workbook.add_format(
                    {'bold': False, 'font_size': 10, 'font_name': 'Times New Roman',
                     'align': 'center', 'valign': 'vcenter', 'text_wrap': 1,
                     'right': 1, 'left': 1, 'top': 1, 'bottom': 1})

                style_left_align_right_left = workbook.add_format(
                    {'bold': False, 'font_size': 8, 'font_name': 'Times New Roman',
                     'align': 'left', 'valign': 'vcenter', 'text_wrap': 1, 'right': 1, 'left': 1,
                     'font_color': '#3339FF'})

                style_left_align_right_left_bottom = workbook.add_format(
                    {'bold': False, 'font_size': 8, 'font_name': 'Times New Roman',
                     'align': 'left', 'valign': 'vcenter', 'text_wrap': 1, 'right': 1, 'left': 1, 'bottom': 1,
                     'font_color': '#3339FF'})
                style_left_align_right_left_top_color = workbook.add_format(
                    {'bold': False, 'font_size': 10, 'font_name': 'Times New Roman',
                     'align': 'left', 'underline': True, 'valign': 'vcenter', 'text_wrap': 1, 'right': 1, 'left': 1,
                     'top': 1, 'font_color': '#3339FF'})
                style_left_align_right_left_top = workbook.add_format(
                    {'bold': False, 'font_size': 10, 'font_name': 'Times New Roman',
                     'align': 'left', 'underline': True, 'valign': 'vcenter', 'text_wrap': 1, 'right': 1, 'left': 1,
                     'top': 1})

                style_header_right = workbook.add_format({'bold': True, 'font_size': 12, 'font_name': 'Times New Roman',
                                                          'align': 'right', 'valign': 'vcenter', 'text_wrap': 1})

                style_center_align_wrap = workbook.add_format(
                    {'bold': False, 'font_size': 10, 'font_name': 'Times New Roman',
                     'align': 'center', 'valign': 'vcenter', 'text_wrap': 1, 'right': 1, 'left': 1, 'top': 1,
                     'bottom': 1})

                style_center_align_wrap_color = workbook.add_format(
                    {'bold': False, 'font_size': 10, 'font_name': 'Times New Roman',
                     'align': 'center', 'valign': 'vcenter', 'text_wrap': 1, 'right': 1, 'left': 1, 'top': 1,
                     'bottom': 1})

                sheet1.set_column(0, 0, 14.00)
                sheet1.set_column(1, 1, 13.00)
                sheet1.set_column(2, 2, 15.00)
                sheet1.set_column(3, 3, 15.00)
                sheet1.set_column(4, 4, 15.00)
                sheet1.set_column(5, 5, 10.00)
                sheet1.set_column(6, 6, 13.00)
                sheet1.set_column(7, 7, 15.00)
                sheet1.set_column(8, 8, 17.00)

                sheet1.fit_to_pages(1, 0)
                sheet1.set_landscape()
                sheet1.header_str = ''
                sheet1.footer_str = ''
                sheet1.set_row(0, 70)

                image_path = get_file_path('petrofac_report/static/src/img/logo.jpg')
                with open(image_path, 'rb') as f:
                    img_bytes = BytesIO(f.read())

                img_bytes.seek(0)

                sheet1.set_row(0, 75)
                sheet1.insert_image(0, 0, 'logo.jpg', {
                    'image_data': img_bytes,
                    'x_scale': 0.6,
                    'y_scale': 0.6,
                    'x_offset': 4,
                    'y_offset': 2,
                })
                row = 0

                # sheet1.insert_image('A1', 'c:/prime4/images/neilbarnett.png',
                #                     {'x_offset': 3, 'y_offset': 4, 'x_scale': 1.3, 'y_scale': 1.2})
                row = 1
                sheet1.merge_range(row, 5, row + 1, 8, 'NBIS-001 - SQS Time Sheet', style_header_new_no_line)
                # row = 2
                # sheet1.merge_range(row,  0, row,8, 'NBIS-001 - SQS Time Sheet', style_header_new_no_line)
                # row = 3
                # sheet1.merge_range(row, row, 0, 12, '', style_header_new_no_line)
                row = 4
                sheet1.merge_range(row, 0, row, 1, '', style_header1)
                sheet1.merge_range(row, 2, row, 8,
                                   'THIS IS NOT AN INVOICE.    Please submit an invoice separately to:   NBIServices@aol.com',
                                   style_header1)
                row = 5
                sheet1.merge_range(row, 0, row, 8, '', style_header_new_no_line)
                # row = 6
                # sheet1.merge_range(row, row, 0, 12, '', style_header_new_no_line)

                row += 9

                sheet1.write(row, 0, 'Visit Date', style_header2)
                sheet1.write(row, 1, 'Name', style_header2)
                sheet1.write(row, 2, 'Report No.', style_header2)
                sheet1.write(row, 3, 'Onsite Hours', style_header2)
                sheet1.write(row, 4, 'Report Hours', style_header2)
                sheet1.write(row, 5, 'Travel Hours', style_header2)
                sheet1.write(row, 6, 'Total Hours', style_header2)
                sheet1.write(row, 7, 'Travel(Miles)', style_header2)
                sheet1.write(row, 8, 'Miscellaneous Expenses', style_header2)
                end_row = row
                row1 = row
                totol_fullday += 1
                unique = ''
                uni = []
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
                    sheet1.write(row, 0, val['start'], style_center_align)
                    sheet1.write(row, 1, self.env.user.name, style_center_align)
                    sheet1.write(row, 2, val['number'], style_center_align)
                    sheet1.write(row, 3, val['hrs_new'], style_center_align_wrap)
                    sheet1.write(row, 4, val['report_hrs'], style_center_align_wrap)
                    sheet1.write(row, 5, val['travl_hrs'], style_center_align_wrap)
                    sheet1.write(row, 6, val['total_hrs_all'], style_center_align_wrap_color)
                    sheet1.write(row, 7, '', style_center_align_wrap_color)
                    sheet1.write(row, 8, val['miscexpen'], style_center_align_wrap_color)

                    total_hrs += val['hrs_new']

                    end_row = row1

                next_row1 = end_row + 1
                formula_total = '=SUM' + '(' + 'G16' + ':' + 'G' + str(next_row1) + ')'
                formula_total_miles = '=SUM' + '(' + 'H16' + ':' + 'H' + str(next_row1) + ')'
                sheet1.write(next_row1, 0, '', style_header)
                sheet1.write(next_row1, 1, '', style_header)
                sheet1.write(next_row1, 2, '', style_header)
                sheet1.write(next_row1, 3, '', style_header)
                sheet1.write(next_row1, 4, '', style_header)
                sheet1.write(next_row1, 5, 'Total Used:', style_center_align)
                sheet1.write(next_row1, 6, formula_total, style_center_align)
                sheet1.write(next_row1, 7, formula_total_miles, style_center_align)
                sheet1.write(next_row1, 8, '', style_center_align)

                next_row = next_row1 + 1
                formula_remain = '=SUM' + '(' + 'G13' + '-' + 'G' + str(next_row) + ')'
                formula_total_cal = '=SUM' + '(' + 'IF(G13<>0' + ',' + 'G' + str(next_row) + '/G13)' + ')'
                sheet1.merge_range(next_row, 0, next_row, 4, 'Field Representative Notes',
                                   style_left_align_right_left_top)
                sheet1.write(next_row, 5, 'Remain Hrs:', style_header_left_no_bold_left)
                sheet1.write(next_row, 6, formula_remain, style_center_align)
                sheet1.write(next_row, 7, formula_total_cal, style_center_align)
                sheet1.write(next_row, 8, 'Percentage of Hours Used', style_header_left_no_bold_left)

                next6_row = next_row + 1
                sheet1.merge_range(next6_row, 5, next6_row, 8, 'Instructions for Completion',
                                   style_left_align_right_left_top_color)

                next33_row = next6_row + 1

                sheet1.merge_range(next33_row, 5, next33_row + 1, 8,
                                   'A Time Sheet must be completed after each visit and a copy attached\n to your surveillance (Inspection or Expediting) report.',
                                   style_left_align_right_left)

                next333_row = next33_row + 2
                sheet1.merge_range(next333_row, 5, next333_row + 1, 8,
                                   'Seperate Individual Time Sheets to be submitted for each Assignment / \nPO being worked on.',
                                   style_left_align_right_left)

                next34_row = next333_row + 2
                sheet1.merge_range(next34_row, 5, next34_row + 1, 8,
                                   'Time claimed for Report Time should reflect detail, length and \ncontent of the report.',
                                   style_left_align_right_left)

                next344_row = next34_row + 2
                sheet1.merge_range(next344_row + 1, 0, next344_row + 1, 4, '', style_left_align_right_left_bottom)
                sheet1.merge_range(next344_row, 5, next344_row + 1, 8,
                                   'Travel Time claimed for should reflect reasonable travel distance \nincurred.',
                                   style_left_align_right_left_bottom)

                next3_row = next344_row + 2

                row = 12

                sheet1.merge_range(row, 0, row, 1, 'NBIS Project No.:', style_header_right)
                sheet1.merge_range(row, 2, row, 3, '', style_header_left_no_bold)
                sheet1.merge_range(row, 4, row, 5, 'Est. Person Hours: ', style_header_right)
                sheet1.write(row, 6, '', style_header_left_no_bold)
                sheet1.write(row, 7, 'Company', style_header_right)
                sheet1.write(row, 8, '', style_header_left_no_bold)

                row = 10

                sheet1.merge_range(row, 0, row, 1, 'Client Project No.:', style_header_right)
                sheet1.merge_range(row, 2, row, 3, self.project_id.name, style_header_left_no_bold)
                sheet1.merge_range(row, 4, row, 5, 'Vendor/Sub ref No.: ', style_header_right)
                sheet1.merge_range(row, 6, row, 8, '', style_header_left_no_bold)
                row = 8

                if len(po_value) > 0:
                    po_ref_number = ', \n'.join(po_value)
                else:
                    po_ref_number = ''

                if (len(po_ref_number) + 25) > 36:
                    height_factor = int((len(po_ref_number) + 25) / 36) + 1

                location_name = calendar_event[0].v_location.name if calendar_event[0].v_location.id != False else ''
                sheet1.merge_range(row, 0, row, 1, 'Client P.O. / Assigment No.:', style_header_right)
                sheet1.merge_range(row, 2, row, 3, po_ref_number, style_header_left_no_bold)
                sheet1.merge_range(row, 4, row, 5, 'Location: ', style_header_right)
                sheet1.merge_range(row, 6, row, 8, location_name, style_header_left_no_bold)

                row = 6
                sheet1.write(row, 0, 'Client :', style_header_right)
                if val['end_client']:
                    sheet1.merge_range(row, 1, row, 3, val['end_client'], style_header_left_no_bold)
                else:
                    sheet1.merge_range(row, 1, row, 3, '', style_header_left_no_bold)
                sheet1.merge_range(row, 4, row, 5, 'Vendor/Subvendor : ', style_header_right)
                sheet1.merge_range(row, 6, row, 8, val['vendor'], style_header_left_no_bold)

                workbook.close()
                out = base64.encodebytes(output.getvalue())
                data.append(('%s_%s_%s.xlsx' % (unique, start, category), out))

        self._create_zip_from_xlsx_data(data)

        report_common_method.send_report_notification(
            self.env,
            self.file_name,
            self.file,
            'neil.barnett.summary.report',
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
            'res_model': 'neil.barnett.summary.report',
            'target': 'new',
            'context': self._context
        }
