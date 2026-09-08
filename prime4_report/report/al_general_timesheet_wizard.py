from odoo import models, fields, api, _
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
from odoo.exceptions import UserError
import calendar
from odoo.tools.misc import file_path as get_file_path
from odoo.addons.project_management import report_common_method


class general_timesheet_report(models.TransientModel):
    _name = 'general.timesheet.report'
    _inherit = 'common.report'
    _description = 'Timesheet Report'

    location_id = fields.Many2one('res.country', string="Location")

    def _get_month_info(self):
        if not self.month_data or len(self.month_data) != 7:
            raise UserError(_("Month format must be MM/YYYY"))

        month = int(self.month_data[:2])
        year = int(self.month_data[3:7])
        from_date_join = str(year) + '-' + str(month) + '-01'
        iter_range = calendar.monthrange(year, month)[1]
        return {
        'iter_range': iter_range,
        'from_date_join': from_date_join,
    }


    def generate_report_excel(self):

        domain, fromdate, todate = self._get_calendar_domain(
            client_code='equasrl',
            include_status=False,
            extra_domain=[]
        )

        calendar_event = self.env['calendar.event'].search(domain, order="start,employee_role,client_of_client_id")
        if not calendar_event:
            raise UserError(_("No Record Found"))

        def equasrl_value_builder(record):
            values = self._build_common_values(record)

            kms_new = record.add_km_mileage1 or 0

            values.update({
                'location': record.v_location.name if record.v_location else '',
                'clients_id': record.client_of_client_id.name if record.client_of_client_id else '',
                'client_id': record.client_id.name if record.client_id else '',
                'hrs_new': record.hrs,
                'kms_new': kms_new,
                'project': record.project_id.name if record.project_id else '',
            })

            return values

        start_values_data = self._group_calendar_records(
            calendar_event, equasrl_value_builder
        )
            

        start_values_data_sort = sorted(start_values_data.items())
        data = []
        count = 0
        for start, categorious in start_values_data_sort:
            for category, records in categorious.items():
                uni = []
                byte_io = BytesIO()
                workbook = xlsxwriter.Workbook(byte_io)
                worksheet = workbook.add_worksheet(category)

                style_header = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})
                style_header_new_left = workbook.add_format(
                    {'font_name': 'Arial', 'bold': True, 'font_size': 8, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})
                style_color_blue_text = workbook.add_format(
                    {'font_name': 'Arial', 'font_color': 'blue', 'bold': True, 'font_size': 8, 'align': 'left', 'valign': 'vcenter',
                     'text_wrap': True, 'border': 1})
                style_left_align = workbook.add_format(
                    {'font_name': 'Arial', 'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'border': 1})
                style_last_line = workbook.add_format({'bottom': 2})
                style_bold_only = workbook.add_format(
                    {'font_name': 'Arial', 'font_size': 10, 'bold': True, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True})

                worksheet.set_column('A:A', 8)
                worksheet.set_column('B:B', 15)
                worksheet.set_column('C:C', 13)
                worksheet.set_column('D:D', 23)
                worksheet.set_column('E:E', 23)
                worksheet.set_column('F:F', 16)
                worksheet.set_column('G:G', 13)
                worksheet.set_column('H:H', 5)
                worksheet.set_column('I:I', 3)
                worksheet.set_column('J:J', 7)
                worksheet.set_column('K:K', 8)

                worksheet.fit_to_pages(1, 1)


                image_path = get_file_path('prime4_report/static/src/img/logo.jpg')
                with open(image_path, 'rb') as f:
                    img_bytes = BytesIO(f.read())

                img_bytes.seek(0)
                worksheet.set_row(0, 75)
                worksheet.insert_image(0, 0,'logo.jpg' , {
                    'image_data': img_bytes,
                    'x_scale': 0.6,
                    'y_scale': 0.6,
                    'x_offset': 4,
                    'y_offset': 2,
                })

                row = 0
                row = 3
                worksheet.merge_range(2, 2, 2, 3, 'ACTIVITIES MONTH OF:', style_header_new_left)
                worksheet.merge_range(4, 2, 4, 3, 'INSPECTOR/AGENCY:', style_header_new_left)
                worksheet.merge_range(4, 4, 4, 5, str(self.inspector_id.ins_name) + '/Prime4 Inspection', style_color_blue_text)
                month_info = self._get_month_info()
                from_date_join = month_info['from_date_join']
                worksheet.merge_range(2, 4, 2, 5, from_date_join, style_color_blue_text)

                worksheet.write(7, 0, 'Day', style_header)
                worksheet.write(7, 1, 'Client', style_header)
                worksheet.write(7, 2, 'Project', style_header)
                worksheet.write(7, 3, 'Vendor/Location', style_header)
                worksheet.write(7, 4, 'Inspector', style_header)
                worksheet.write(7, 5, 'Activity', style_header)
                worksheet.write(7, 6, 'Day', style_header)
                worksheet.write(7, 7, 'Hours', style_header)
                worksheet.write(7, 8, 'Km', style_header)
                worksheet.write(7, 9, 'Expenses', style_header)
                iter_row = 8
                unique = ''
                for i in range(10):
                    worksheet.write(5, i, '', style_last_line)
                day_count = total_hours = total_kms = total_expenses = 0.0
                total_kms = 0
                iter_range = month_info['iter_range']
                for i in range(1, iter_range + 1):
                    month = self.month_data[0:2]
                    year = self.month_data[3:7]
                    day = '0' + str(i) if i < 10 else str(i)
                    from_date_join = str(year) + '-' + str(month) + '-' + str(day)
                    from_date = datetime.strptime(from_date_join, "%Y-%m-%d")
                    from_date_end = from_date_join + ' 23:59:59'
                    day_string = from_date.strftime("%A")

                    client_name = ''
                    project_name = ''
                    vendor_name = ''
                    location_name = ''
                    inspector_name = ''
                    activity_name = ''
                    # day_string =   ''
                    hours = ''
                    km = ''
                    expenses = ''
                    vendor_location = ''
                    client_start_row = start_row = 0
                    client_end_row = end_row = 0
                    merge_start = iter_row

                    if len(calendar_event) > 0:
                        fresh_count = 0
                        for ce in records:
                            un = ce['unique_no']
                            txn = ce['txn']
                            part = str(un) if un else str(txn)
                            if part not in uni:
                                uni.append(part)
                                unique += part + '_'


                            count+=1
                            client_name = ce['client_id']
                            project_name = ce['project']
                            inspector_name = ce['employee']
                            activity_name = ce['category']
                            day_string = day_string
                            hours = ce['hrs_new']
                            km = ce['kms_new']
                            vendor_name = ce['vendor']
                            location_name = ce['location']
                            vendor_location = str(vendor_name)
                            vendor_location += '/' if location_name != '' else ''
                            vendor_location += str(location_name) + str('\n')

                            len_vendor_location = len(vendor_location)
                            len_client_name = len(ce['clients_id']) if ce['clients_id'] else 0
                            len_project_name = len(ce['project'])
                            if len_vendor_location > len_client_name and len_vendor_location > len_project_name:
                                height_factor = int(len_vendor_location / 10)
                            elif len_client_name > len_vendor_location and len_client_name > len_project_name:
                                height_factor = int(len_client_name / 5)
                            else:
                                height_factor = int(len_project_name / 5)

                            if height_factor > 0:
                                height = height_factor * 300
                            else:
                                height = 500

                            # worksheet.row(iter_row).height = int(height / len(calendar_event))
                            if activity_name != ce['employee_role']:
                                if fresh_count != 0:
                                    worksheet.write(iter_row,5,activity_name, style_left_align)

                                start_row = iter_row
                                end_row = iter_row
                            if client_name != ce['clients_id']:
                                if fresh_count != 0:
                                    worksheet.merge_range(client_start_row, 1, iter_row - 1, 1, client_name, style_left_align)
                                    worksheet.write(iter_row, 1,  client_name, style_left_align)

                                client_start_row = iter_row
                                client_end_row = iter_row

                            expenses = 0.0

                            total_hours += hours
                            total_kms += km
                            total_expenses += expenses

                            worksheet.write(iter_row, 6, day_string, style_left_align)
                            worksheet.write(iter_row, 7, hours, style_left_align)
                            worksheet.write(iter_row, 8, km, style_left_align)
                            worksheet.write(iter_row, 9, expenses if expenses > 0.0 else '', style_left_align)


                        worksheet.write(iter_row,0,  i, style_left_align)
                        worksheet.write(iter_row, 2, project_name, style_left_align)
                        worksheet.write(iter_row, 3, vendor_location, style_left_align)
                        worksheet.write(iter_row, 4,  inspector_name, style_left_align)
                        iter_row += 1
                        fresh_count += 1
                        day_count += 1
                        if start_row != 0 and start_row < (iter_row - 1):
                            worksheet.merge_range(start_row, 5, iter_row - 1, 5, activity_name, style_left_align)
                        else:
                            worksheet.write(iter_row - 1, 5, activity_name, style_left_align)
                        if client_start_row != 0 and client_start_row < (iter_row - 1):
                            worksheet.merge_range(client_start_row, 1, iter_row - 1, 1, client_name, style_left_align)
                        else:
                            worksheet.write(iter_row - 1, 1, client_name, style_left_align)
                    else:
                        worksheet.write(iter_row, 0, i, style_left_align)
                        client_name = ''
                        project_name = ''
                        vendor_name = ''
                        location_name = ''
                        inspector_name = ''
                        activity_name = ''
                        day_string = ''
                        hours = ''
                        km = ''
                        expenses = 0.0
                        vendor_location = ''
                        # iter_row += 1
                        worksheet.write(iter_row, 0, i, style_left_align)
                        worksheet.write(iter_row, 1, client_name, style_left_align)
                        worksheet.write(iter_row, 2, project_name, style_left_align)
                        worksheet.write(iter_row, 3, vendor_location, style_left_align)
                        worksheet.write(iter_row, 4, inspector_name, style_left_align)
                        worksheet.write(iter_row, 5, activity_name, style_left_align)
                        worksheet.write(iter_row, 6, day_string, style_left_align)
                        worksheet.write(iter_row, 7, hours, style_left_align)
                        worksheet.write(iter_row, 8, km, style_left_align)
                        worksheet.write(iter_row, 9, expenses if expenses > 0.0 else '', style_left_align)
                        iter_row += 1

                iter_row += 1
                # worksheet.row(iter_row).height = 500
                worksheet.write(iter_row, 0, 'Expenses resume', style_header)
                worksheet.write(iter_row, 1, 'Nr.', style_header)

                worksheet.write(iter_row, 2, '$/Cad', style_header)
                worksheet.write(iter_row, 3, 'Total', style_header)
                worksheet.write(iter_row, 4, '', style_header)
                worksheet.merge_range(iter_row, 5, iter_row, 9, 'Total to be invoiced', style_header)
                worksheet.write(iter_row + 1, 0, 'Days', style_header)
                worksheet.write(iter_row + 2, 0, 'Hours', style_header)
                worksheet.write(iter_row + 3, 0, 'Km', style_header)
                worksheet.write(iter_row + 4, 0, 'Expenses', style_header)
                worksheet.write(iter_row + 1, 1, '', style_header)
                worksheet.write(iter_row + 2, 1, '', style_header)
                worksheet.write(iter_row + 3, 1, '', style_header)
                worksheet.write(iter_row + 4, 1, '', style_header)
                worksheet.write(iter_row + 1, 2, '', style_header)
                worksheet.write(iter_row + 2, 2, '', style_header)
                worksheet.write(iter_row + 3, 2, '', style_header)
                worksheet.write(iter_row + 4, 2, '', style_header)
                worksheet.write(iter_row + 1, 3, day_count if day_count > 0.0 else '', style_left_align)
                worksheet.write(iter_row + 2, 3, total_hours if total_hours > 0.0 else '', style_left_align)
                worksheet.write(iter_row + 3, 3, total_kms if total_kms > 0.0 else '', style_left_align)
                worksheet.write(iter_row + 4, 3, total_expenses if total_expenses > 0.0 else '', style_left_align)
                worksheet.write(iter_row + 4, 4, '', style_header)
                worksheet.merge_range(iter_row + 7, 1, iter_row + 7, 2, 'INSPECTOR SIGNATURE', style_bold_only)
                worksheet.merge_range(iter_row + 7, 5, iter_row + 7, 8, 'E.QU.A. AUTHORIZATION', style_bold_only)
                worksheet.merge_range(iter_row + 9, 1, iter_row + 9, 2, '', style_header)
                worksheet.merge_range(iter_row + 9, 5, iter_row + 9, 8, '', style_header)
                worksheet.merge_range(iter_row + 1, 5, iter_row + 4, 9, '', style_header)

                workbook.close()
                file_data = byte_io.getvalue()
                file_content = base64.b64encode(file_data)
                data.append(('%s_%s_%s.xlsx' % (unique, start, category), file_content))

        self._create_zip_from_xlsx_data(data)

        report_common_method.send_report_notification(
            self.env,
            self.file_name,
            self.file,
            'general.timesheet.report',
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
            'views': [(self.env.ref('prime4_report.general_timesheet_wizard_report_view').id, 'form')],
            'res_model': 'general.timesheet.report',
            'target': 'new',
            'context': self._context
        }
    def generate_report_excel_spx_flow(self):
        domain, fromdate, todate = self._get_calendar_domain(
            client_code='spxflow',
            include_status=False,
            extra_domain=[
                ('v_location', '=', self.location_id.id) if self.location_id else ()
            ]
        )
        calendar_event = self.env['calendar.event'].search(domain, order="start,employee_role,client_of_client_id")
        if not calendar_event:
            raise UserError(_("No Record Found"))

        def spxflow_value_builder(record):
            values = self._build_common_values(record)
            return values

        start_values_data = self._group_calendar_records(
            calendar_event, spxflow_value_builder
        )

        start_values_data_sort = sorted(start_values_data.items())
        data=[]
        for start, categorious in start_values_data_sort:
            unique =''
            for category, records in categorious.items():
                uni = []
                byte_io = BytesIO()
                workbook = xlsxwriter.Workbook(byte_io)
                worksheet = workbook.add_worksheet(category)

                style_header_new_left = workbook.add_format(
                    {'font_name': 'Arial','bold': True, 'font_size': 8, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})
                style_new_left = workbook.add_format(
                    {'font_name': 'Arial', 'font_size': 8, 'align': 'left', 'valign': 'vcenter',
                     'text_wrap': True,
                     })
                style_last_line = workbook.add_format({'bottom': 2})
                style_bold_only = workbook.add_format(
                    {'font_name': 'Arial','font_size': 10, 'bold': True, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True})
                style_center_align = workbook.add_format(
                    {'font_name': 'Arial','bold': True, 'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'text_wrap': True})
                style_center_align_wrap = workbook.add_format(
                    {'font_name': 'Arial','bold': True, 'font_size': 40, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                     'border': 1})

                worksheet.set_column('A:A', 8)
                worksheet.set_column('B:B', 22)
                worksheet.set_column('C:C', 13)
                worksheet.set_column('D:D', 5)
                worksheet.set_column('E:E', 7)
                worksheet.set_column('F:F', 16)
                worksheet.set_column('G:G', 13)
                worksheet.set_column('H:H', 3)
                worksheet.set_column('I:I', 3)
                worksheet.set_column('J:J', 7)
                worksheet.set_column('K:K', 8)

                worksheet.set_row(1, 50)

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

                row = 5
                worksheet.write(row, 1, 'Name', style_header_new_left)
                worksheet.write(row, 2, 'LPO No.', style_header_new_left)
                row += 1
                worksheet.write(row, 1, '', style_header_new_left)
                worksheet.write(row, 2, '', style_header_new_left)
                head_col = 3
                month_info = self._get_month_info()
                iter_range = month_info['iter_range']
                for i in range(1, iter_range + 1):
                    worksheet.set_column(head_col, head_col, 3.2)
                    worksheet.write(row, head_col, i, style_header_new_left)
                    worksheet.write(row - 1, head_col, '', style_header_new_left)
                    head_col += 1
                worksheet.merge_range(1, 2, 1, iter_range + 2, 'Lindinger Inspection Services', style_center_align_wrap)
                month = self.month_data[0:2]
                year = self.month_data[3:7]
                day = '0' + str(i) if i < 10 else str(i)
                from_date_join = str(year) + '-' + str(month) + '-' + str(day)
                from_date = datetime.strptime(from_date_join, "%Y-%m-%d")
                month_string = from_date.strftime('%B')
                month_string = month_string.upper()

                worksheet.merge_range(3, 0, 3, iter_range + 2,
                                   'TIME SHEET FOR THE MONTH OF ' + str(month_string) + ' ' + str(year), style_center_align)

                iter_row = 7
                purchase_id = ''
                for event in records:
                    un = event['unique_no']
                    txn = event['txn']
                    part = str(un) if un else str(txn)
                    if part not in uni:
                        uni.append(part)
                        unique += part + '_'
                    if purchase_id != event['purchase']:
                        purchase_id = event['purchase']
                        row += 1
                        worksheet.write(row, 2, event['purchase'],style_new_left)
                        worksheet.write(row, 1, str(self.env.user.name) if self.env.user.name else '',style_new_left)


                row += 1
                line_end_row = row

                row += 3
                worksheet.write(row, 1, 'Vendor Name:', style_bold_only)
                worksheet.write(row, 2, self.vendor_id.name if self.vendor_id.name else '', style_bold_only)
                worksheet.merge_range(row, 7, row, 12, 'Name of Inspector:', style_bold_only)
                worksheet.merge_range(row, 13, row, 18, str(self.env.user.name) if self.env.user.name else '',style_new_left)
                worksheet.merge_range(row, 19, row, 23, 'Signature of Inspector:', style_bold_only)
                row += 1
                worksheet.write(row, 1, 'Location', style_bold_only)
                worksheet.write(row, 2, self.location_id.name if self.location_id.name else '',style_new_left)
                row += 2
                worksheet.merge_range(row, 7, row, 12, 'Name of Approving Authority :', style_bold_only)
                worksheet.merge_range(row, 19, row, 23, 'Signature of Approving Authority : ', style_bold_only)
                row += 1
                worksheet.write(row, 7, 'Date:', style_bold_only)
                row += 2
                worksheet.write(row, 1, 'X - Absent', style_bold_only)
                worksheet.write(row + 1, 1, 'F - Friday', style_bold_only)
                worksheet.write(row + 2, 1, 'H - Holiday', style_bold_only)

                for j in range(iter_range + 3):
                    worksheet.write(3, j, '', style_last_line)
                    worksheet.write(line_end_row, j, '', style_last_line)
                    worksheet.write(row + 4, j, '', style_last_line)
                workbook.close()
                file_data = byte_io.getvalue()
                file_content = base64.b64encode(file_data)
                data.append(('%s_%s_%s.xlsx' % (unique, start, category), file_content))

        self._create_zip_from_xlsx_data(data)

        report_common_method.send_report_notification(
            self.env,
            self.file_name,
            self.file,
            'general.timesheet.report',
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
            'views': [(self.env.ref('prime4_report.general_timesheet_wizard_report_view').id, 'form')],
            'res_model': 'general.timesheet.report',
            'target': 'new',
            'context': self._context
        }
