# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from io import BytesIO
import base64
import zipfile
import os
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.exceptions import UserError
import xlsxwriter
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from odoo.tools.misc import file_path as get_file_path


@lru_cache(maxsize=1)
def _get_logo_bytes():
    image_path = get_file_path('zip_reports/static/src/img/logo.jpg')
    with open(image_path, 'rb') as f:
        return f.read()


class ZipReports(models.TransientModel):
    _name = "zip.reports"
    _inherit = 'common.report'
    _description = "Zip Reports"

    coordinator_id = fields.Many2one('res.users', string="Coordinator", domain=lambda self: [("groups_id", "=",
                                                self.env.ref("project_management.group_p4_coordinator").id)])

    def _prepare_report_data(self, events):

        start_values_data = {}
        purchase_new = []
        for record in events:
            purchase = record.purchase_id.name if record.purchase_id else ''

            vendor = record.vendor_id.name if record.vendor_id else ''

            if record.sub_vendor:
                sub_names = ', '.join(record.sub_vendor.mapped('name'))
                vendor = f"Vendor:{vendor}\nSubvendor:{sub_names}"
            # if record.sub_vendor:
            #     vendor = f"Vendor:{vendor}\nSubvendor:{record.sub_vendor.name}"

            start = record.start.strftime("%d/%m/%Y") if record.start else ''
            category_label = dict(record._fields['category_expenses'].selection).get(record.category_expenses, '')
            values = {
                'purchase': purchase,
                'vendor': vendor,
                'employee': record.employee or '',
                'employee_role': f"{record.employee_role.name if record.employee_role else ''}\n{category_label}",
                'start': start,
                'number': record.rpt_number or '',
                'notification_no': record.notification_no or '',
                'eigl_person': record.eigl_person_id.name if record.eigl_person_id else '',
                'overnight': "Overnight Expenses" if record.overnight_expense else "No Overnight Expenses",
                'extra_hrs_new': record.extra_hrs or '',
                'kms_new': record.kms or '',
                'allday': record.allday,
                'abortive_visit': record.abortive_visit,
                'location': record.v_location.name if record.v_location else '',
                'approver': record.approver.name if record.approver else '',
                'is_worked_on_holiday_sunday': record.is_worked_on_holiday_sunday if hasattr(record, 'is_worked_on_holiday_sunday') else False,
                'is_worked_on_extended_hours': record.is_worked_on_extended_hours if hasattr(record, 'is_worked_on_extended_hours') else False,
                'skip_man_day': record.skip_man_day if hasattr(record, 'skip_man_day') else False,
            }
            if start:
                start_date = datetime.strptime(start, "%d/%m/%Y")
                start_values_data.setdefault(start_date, []).append(values)

            if purchase:
                purchase_new.append(purchase)

        return start_values_data, purchase_new

    def _write_excel_extra_section(self, workbook, worksheet, formats, start_row, title, bg_color, rows):
        """Render an extra single-day table (e.g. "Working on Holiday / Sunday"
        or "Working on Extended Hours") below the main timesheet table, starting
        at ``start_row``. Returns the row index of the section's total row.

        Both sections share an identical layout; only the title and the header
        background colour differ, hence the single parameterised helper.
        """
        centered_format = formats['centered']
        centered_wrap_format = formats['centered_wrap']
        header_format = formats['header']
        color_format = formats['color']
        section_header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'border': 1, 'font_size': 8, 'font_name': 'Arial',
            'text_wrap': True, 'bg_color': bg_color,
        })

        row = start_row
        worksheet.merge_range(row, 0, row, 11, title, section_header_format)
        row += 1

        # Column sub-headers (OD/HD columns 8-9 are merged and left blank here).
        labels = ['P.O. Nr.', 'VENDOR', 'INSPECTOR', 'ROLE', 'VISIT DATE',
                  'REPORT NUMBER', 'NOTIFICATION NO', 'EICM', '', '',
                  'Expenses\nEUR', 'Expenses\nDescription']
        for col, label in enumerate(labels):
            if col == 8:
                worksheet.merge_range(row, 8, row, 9, '', section_header_format)
            elif col == 9:
                continue
            else:
                worksheet.write(row, col, label, section_header_format)
        row += 1

        # OD / HD labels.
        for col, label in enumerate(['', '', '', '', '', '', '', '', 'OD', 'HD', '', '']):
            worksheet.write(row, col, label, color_format if col in (8, 9) else header_format)
        row += 1

        total_od = 0
        for val in rows:
            worksheet.write(row, 0, val['purchase'], centered_wrap_format)
            worksheet.write(row, 1, val['vendor'], centered_wrap_format)
            worksheet.write(row, 2, val['employee'], centered_format)
            worksheet.write(row, 3, val['employee_role'], centered_format)
            worksheet.write(row, 4, val['start'], centered_format)
            worksheet.write(row, 5, val['number'], centered_format)
            worksheet.write(row, 6, val['notification_no'], centered_format)
            worksheet.write(row, 7, val['eigl_person'], centered_format)
            od_value = '-' if val.get('skip_man_day') else 1
            worksheet.write(row, 8, od_value, centered_format)
            worksheet.write(row, 9, '-', centered_format)
            worksheet.write(row, 10, '-', centered_format)
            worksheet.write(row, 11, val['overnight'], centered_format)
            total_od += 0 if val.get('skip_man_day') else 1
            row += 1

        # Total row.
        for col in range(12):
            if col == 8:
                worksheet.write(row, col, '-' if total_od == 0 else str(total_od), centered_format)
            elif col == 9:
                worksheet.write(row, col, '-', centered_format)
            else:
                worksheet.write(row, col, '', centered_format)
        return row

    def generate_report_excel_tcm(self, events, report_data=None):
        res = {}
        # Create a new workbook and worksheet
        byte_io = BytesIO()
        workbook = xlsxwriter.Workbook(byte_io)
        worksheet = workbook.add_worksheet('Timesheet Report')

        # Set column widths
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

        # Define formats
        bold_centered_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 8, 'font_name': 'Arial', 'text_wrap': True})
        bold_left_format = workbook.add_format({'bold': True, 'align': 'left', 'valign': 'vcenter', 'border': 1, 'font_size': 8, 'font_name': 'Arial', 'text_wrap': True})
        bold_right_format = workbook.add_format({'bold': True, 'align': 'right', 'valign': 'vcenter', 'border': 1, 'font_size': 8, 'font_name': 'Arial', 'text_wrap': True})
        centered_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 8, 'font_name': 'Arial', 'text_wrap': True})
        centered_wrap_format = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1, 'font_size': 8, 'font_name': 'Arial'})
        header_format = workbook.add_format(
            {'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_size': 8, 'font_name': 'Arial', 'text_wrap': True})
        color_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#ffffbd', 'font_size': 8, 'font_name': 'Arial', 'text_wrap': True})

        company = self.env.company
        img_bytes = BytesIO(_get_logo_bytes())

        img_bytes.seek(0)
        worksheet.insert_image(0, 0, 'logo.jpg', {
            'image_data': img_bytes,
            'x_scale': 0.4,
            'y_scale': 0.4,
            'x_offset': 4,
            'y_offset': 2,
        })

        # Writing some metadata
        worksheet.write(3, 4, 'Contract', bold_centered_format)

        # Set contract number depending on the employee's role
        if events[0].employee_role.name == 'inspector':
            contract_no = events[0].project_id.inspection_contract_no
        elif events[0].employee_role.name == 'expeditor':
            contract_no = events[0].project_id.expediting_contract_no
        else:
            contract_no = events[0].project_id.inspection_contract_no

        worksheet.write(3, 5, contract_no or '', color_format)
        worksheet.merge_range(3, 7, 3, 8, 'Month', bold_left_format)

        # Additional info (like agency, country, etc.)
        worksheet.write(4, 0, 'Agency', bold_centered_format)
        worksheet.write(4, 1, company.name, color_format)
        worksheet.merge_range(4, 7, 4, 8, 'Country', bold_left_format)

        # Add table headers
        worksheet.write(5, 0, 'P.O. Nr.', header_format)
        worksheet.write(5, 1, 'VENDOR', header_format)
        worksheet.write(5, 2, 'INSPECTOR', header_format)
        worksheet.write(5, 3, 'ROLE', header_format)
        worksheet.write(5, 4, 'VISIT DATE', header_format)
        worksheet.write(5, 5, 'REPORT NUMBER', header_format)
        worksheet.write(5, 6, 'NOTIFICATION NO',header_format)
        worksheet.write(5, 7, 'EICM', header_format)
        worksheet.merge_range(5, 8, 5, 9, '', color_format)
        worksheet.write(5, 10, 'Expenses \nEUR', header_format)
        worksheet.write(5, 11, 'Expenses \nDescription', header_format)

        worksheet.write(6, 0, '', header_format)
        worksheet.write(6, 1, '', header_format)
        worksheet.write(6, 2, '', header_format)
        worksheet.write(6, 3, '', header_format)
        worksheet.write(6, 4, '', header_format)
        worksheet.write(6, 5, '', header_format)
        worksheet.write(6, 6, '', header_format)
        worksheet.write(6, 7, '', header_format)
        worksheet.write(6, 8, 'OD', color_format)
        worksheet.write(6, 9, 'HD', color_format)
        worksheet.write(6, 10, '', header_format)
        worksheet.write(6, 11, '', header_format)

        row = 6
        end_row = row

        start_values_data, purchase_new = report_data if report_data is not None else self._prepare_report_data(events)

        # Process and write rows
        totol_fullday = 0
        totol_halfday = '-'
        for start_date, records in sorted(start_values_data.items()):
            main_records = [
                v for v in records
                if not v.get('is_worked_on_holiday_sunday') and not v.get('is_worked_on_extended_hours')
            ]
            if not main_records:
                continue
            end_row = row
            row1 = row
            if not any(v.get('skip_man_day') for v in main_records):
                totol_fullday += 1
            multiple_records = len(main_records) > 1
            for val in main_records:
                row += 1
                start_row = end_row + 1
                row1 += 1
                worksheet.write(row, 0, val['purchase'], centered_wrap_format)
                worksheet.write(row, 1, val['vendor'], centered_wrap_format)
                worksheet.write(row, 2, val['employee'], centered_format)
                worksheet.write(row, 3, val['employee_role'], centered_format)
                worksheet.write(row, 5, val['number'], centered_format)
                worksheet.write(row, 6, val['notification_no'], centered_format)
                worksheet.write(row, 7, val['eigl_person'], centered_format)
                worksheet.write(row, 9, '-', centered_format)
                worksheet.write(row, 10, '-', centered_format)
                worksheet.write(row, 11, val['overnight'], centered_format)
            end_row = row1
            if multiple_records:
                od_value = '-' if any(v.get('skip_man_day') for v in main_records) else 1
                worksheet.merge_range(start_row, 8, end_row, 8, od_value, centered_format)
                worksheet.merge_range(start_row, 4, end_row, 4, str(start_date.strftime("%d/%m/%Y")), centered_format)
            else:
                od_value = '-' if val.get('skip_man_day') else 1
                worksheet.write(start_row, 8, od_value, centered_format)
                worksheet.write(start_row, 4, str(start_date.strftime("%d/%m/%Y")), centered_format)

        next_row = end_row + 1
        worksheet.write(next_row, 0, '', centered_format)
        worksheet.write(next_row, 1, '', centered_format)
        worksheet.write(next_row, 2, '', centered_format)
        worksheet.write(next_row, 3, '', centered_format)
        worksheet.write(next_row, 4, '', centered_format)
        worksheet.write(next_row, 5, '', centered_format)
        worksheet.write(next_row, 6, '', centered_format)
        worksheet.write(next_row, 7, '', centered_format)
        worksheet.write(next_row, 8, '-' if totol_fullday == 0 else str(totol_fullday), centered_format)
        worksheet.write(next_row, 9, str(totol_halfday), centered_format)
        worksheet.write(next_row, 10, '', centered_format)
        worksheet.write(next_row, 11, '', centered_format)

        # Collect holiday and extended hours rows
        all_rows_flat = [val for records in start_values_data.values() for val in records]
        holiday_rows = [v for v in all_rows_flat if v.get('is_worked_on_holiday_sunday')]
        ext_rows = [v for v in all_rows_flat if v.get('is_worked_on_extended_hours')]

        # Both extra tables share the same layout, so render them through one
        # helper. Each is anchored two rows below the previous content.
        extra_formats = {
            'centered': centered_format,
            'centered_wrap': centered_wrap_format,
            'header': header_format,
            'color': color_format,
        }
        section_row = next_row
        if holiday_rows:
            section_row = self._write_excel_extra_section(
                workbook, worksheet, extra_formats, next_row + 2,
                'Working on Holiday / Sunday', '#92D050', holiday_rows,
            )
        if ext_rows:
            anchor = (section_row + 2) if holiday_rows else (next_row + 2)
            section_row = self._write_excel_extra_section(
                workbook, worksheet, extra_formats, anchor,
                'Working on extended hours', '#FFFF00', ext_rows,
            )

        # Project details and metadata
        if events:
            calendar_start_date = events[0].start.strftime("%b-%Y") if events[0].start else ''
            worksheet.write(3, 6, calendar_start_date, bold_right_format)

        purchase_string = ", ".join(set(purchase_new))
        project_info = f"{events[0].project_id.name}; PO# {purchase_string}"
        worksheet.write(4, 4, 'Project', bold_centered_format)
        worksheet.write(4, 5, project_info, bold_centered_format)
        worksheet.write(4, 6, events[0].v_location.name if events[0].v_location else '', bold_right_format)

        # Save the Excel file
        workbook.close()
        return byte_io.getvalue()

    def generate_report_excel_turkstream(self, events, report_data=None):
        res = {}
        byte_io = BytesIO()
        workbook = xlsxwriter.Workbook(byte_io)
        worksheet = workbook.add_worksheet('Timesheet Report')

        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 12)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 25)
        worksheet.set_column('H:H', 8)
        worksheet.set_column('I:I', 8)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 25)

        style_header_new_no_line = workbook.add_format(
            {'bold': True, 'font_size': 8, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'border': 0})
        style_header_left = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 10, 'align': 'left', 'valign': 'vcenter',
             'text_wrap': True, 'border': 1})
        style_header2 = workbook.add_format(
            {'bold': True, 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
             'bg_color': '#99CCFF', 'border': 1})
        style_center_align = workbook.add_format(
            {'font_name': 'Calibri', 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'text_wrap': True})
        style_center_align_wrap = workbook.add_format(
            {'font_name': 'Calibri', 'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
             'border': 1})
        style_header = workbook.add_format(
            {'bold': True, 'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1})
        style_left_align = workbook.add_format(
            {'font_name': 'Calibri', 'font_size': 11, 'align': 'left', 'valign': 'vcenter', 'border': 1, 'text_wrap': True})
        style_left_align_color = workbook.add_format(
            {'font_name': 'Calibri', 'font_size': 11, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True,
             'bg_color': '#99CCFF', 'border': 1})
        style_header1 = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 14, 'bold': True, 'align': 'center', 'valign': 'vcenter',
             'text_wrap': True, 'border': 1})

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
        worksheet.merge_range(row, 1, row, 10, events[0].project_id.service_order_no_ids.name, style_header_left)

        row = 8
        worksheet.write(row, 0, 'Name of Inspector', style_header_left)
        worksheet.merge_range(row, 1, row, 10, events[0].employee, style_header_left)

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

        start_values_data, purchase_new = report_data if report_data is not None else self._prepare_report_data(events)
        total = 0
        total_abortive = 0
        totol_fullday = 0
        totol_halfday = '-'
        start_values_data_sort = sorted(start_values_data.items())
        for vals in start_values_data_sort:
            end_row = row
            row1 = row

            for val in vals[1]:

                row += 1
                start_row = end_row + 1
                row1 += 1
                worksheet.write(row, 0, val['start'], style_center_align)
                worksheet.write(row, 1, val['purchase'], style_center_align_wrap)
                worksheet.write(row, 2, val['vendor'], style_center_align_wrap)
                worksheet.write(row, 3, val['location'], style_center_align_wrap)
                worksheet.write(row, 4, val['employee_role'], style_center_align_wrap)
                worksheet.write(row, 5, val['number'], style_center_align)

                if val['abortive_visit']:
                    worksheet.write(row, 6, 'Abortive', style_center_align)
                    total_abortive += 1
                elif val.get('skip_man_day'):
                    worksheet.write(row, 6, 0, style_center_align)
                elif val['allday']:
                    worksheet.write(row, 6, 1.0, style_center_align)
                    total += 1
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
        worksheet.merge_range(next3_row, 0, next3_row, 1, 'Name of Aprroving Authority:', style_header_left)
        worksheet.merge_range(next3_row, 2, next3_row, 4, val['approver'], style_header_left)

        worksheet.write(next3_row, 5, '', style_header)

        worksheet.merge_range(next3_row, 6, next3_row, 10, 'Signature of Approving Authority:', style_header_left)

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
        if events[0]:
            if events[0].start:
                calendar_start_date = events[0].start.strftime("%b-%Y") if events[0].start else ''
            else:
                calendar_start_date = ''
            worksheet.merge_range(row, 0, row, 10, 'Timesheet for the month of ' + calendar_start_date, style_header1)
        else:
            worksheet.write(5, 5, '', style_header1)


        next5_row = next4_row + 2

        # img = Image.open("c:\ISO9001_GB__RGB (1).png")
        # image_parts = img.split()
        # r = image_parts[0]
        # g = image_parts[1]
        # b = image_parts[2]
        # img = Image.merge("RGB", (r, g, b))
        # fo = BytesIO()
        # img.save('imagetoadd1.bmp')
        # sheet1.insert_bitmap('imagetoadd1.bmp', next5_row,4, 4)

        next6_row = next5_row + 4

        # img = Image.open("c:\logo bottom.png")
        # image_parts = img.split()
        # r = image_parts[0]
        # g = image_parts[1]
        # b = image_parts[2]
        # img = Image.merge("RGB", (r, g, b))
        # fo = BytesIO()
        # img.save('imagetoadd1.bmp')
        # sheet1.insert_bitmap('imagetoadd1.bmp', next6_row, 1, 1,scale_x = 1.1, scale_y = .7)

        string = ""
        for i, purchase in enumerate(set(purchase_new)):
            if i == 0:
                string += purchase
            elif i % 2 != 0 and i != 0:
                string += ", " + purchase
            else:
                string += ", \n" + purchase

        workbook.close()
        return byte_io.getvalue()

    def generate_report_pdf_tcm(self, events, report_data=None, txn_str=None):

        start_values_data, purchase_new = report_data if report_data is not None else self._prepare_report_data(events)

        company = self.env.company

        # contract logic (same as Excel)
        if events[0].employee_role.name == 'inspector':
            contract_no = events[0].project_id.inspection_contract_no
        elif events[0].employee_role.name == 'expeditor':
            contract_no = events[0].project_id.expediting_contract_no
        else:
            contract_no = events[0].project_id.inspection_contract_no

        month = events[0].start.strftime("%b-%Y") if events[0].start else ''

        purchase_string = ", ".join(set(purchase_new))
        project_info = f"{events[0].project_id.name}; PO# {purchase_string}"
        rows = []
        total_full_day = 0

        for start_date, records in sorted(start_values_data.items()):
            # For TCM: exclude records that belong only to the separate tables
            main_records = [
                rec for rec in records
                if not rec.get('is_worked_on_holiday_sunday') and not rec.get('is_worked_on_extended_hours')
            ]
            if not main_records:
                continue

            od_value = 0 if any(rec.get('skip_man_day') for rec in main_records) else 1
            total_full_day += od_value

            count = len(main_records)

            for i, rec in enumerate(main_records):
                row = rec.copy()
                row['od_value'] = '-' if not od_value else od_value
                row['is_first_in_group'] = (i == 0)
                row['is_last_in_group'] = (i == count - 1)
                rows.append(row)

        logo = base64.b64encode(_get_logo_bytes()).decode()

        if txn_str is None:
            unique_txns = list(dict.fromkeys(e.txn for e in events if e.txn))
            txn_str = ', '.join(unique_txns)

        # Collect flat list of all row dicts (with boolean flags already set)
        all_rows_flat = [rec for records in start_values_data.values() for rec in records]
        holiday_rows = []
        holiday_total_od = 0
        for r in all_rows_flat:
            if r.get('is_worked_on_holiday_sunday'):
                row = r.copy()
                row['od_value'] = '-' if r.get('skip_man_day') else 1
                holiday_rows.append(row)
                holiday_total_od += 0 if r.get('skip_man_day') else 1
        ext_hours_rows = []
        ext_total_od = 0
        for r in all_rows_flat:
            if r.get('is_worked_on_extended_hours'):
                row = r.copy()
                row['od_value'] = '-' if r.get('skip_man_day') else 1
                ext_hours_rows.append(row)
                ext_total_od += 0 if r.get('skip_man_day') else 1
        pdf_data = {
            'rows': rows,
            'contract_no': contract_no,
            'month': month,
            'agency': company.name,
            'country': events[0].v_location.name if events[0].v_location else '',
            'project': project_info,
            'total_full_day': '-' if total_full_day == 0 else total_full_day,
            'logo': logo,
            'subject': events[0].name if events else '',
            'txn_str': txn_str,
            'holiday_rows': holiday_rows,
            'holiday_total_od': '-' if holiday_total_od == 0 else holiday_total_od,
            'ext_hours_rows': ext_hours_rows,
            'ext_total_od': '-' if ext_total_od == 0 else ext_total_od,
            'vendor_name': events[0].vendor_id.name if events[0].vendor_id else '',
            'inspector_name': events[0].employee or '',
        }
        res_ids = events.ids if hasattr(events, 'ids') else [e.id for e in events]
        pdf, _ = self.env['ir.actions.report']._render_qweb_pdf(
            'zip_reports.report_timesheet_pdf_tcm',
            res_ids,
            data=pdf_data
        )
        return pdf

    def generate_report_pdf_turkstream(self, events, report_data=None, txn_str=None):

        start_values_data, purchase_new = report_data if report_data is not None else self._prepare_report_data(events)

        rows = []
        total = 0
        total_abortive = 0

        for start_date, records in sorted(start_values_data.items()):

            for i, rec in enumerate(records):

                row = rec.copy()
                # DAYS calculation (same as Excel)
                if rec.get('abortive_visit'):
                    row['days'] = 'Abortive'
                    row['od_value'] = 0
                    total_abortive += 1
                elif rec.get('skip_man_day'):
                    row['days'] = 0
                    row['od_value'] = 0
                elif rec.get('allday'):
                    row['days'] = 1
                    row['od_value'] = 1
                    total += 1
                else:
                    row['days'] = 0.5
                    row['od_value'] = 0.5
                    total += 0.5

                rows.append(row)
        if txn_str is None:
            unique_txns = list(dict.fromkeys(e.txn for e in events if e.txn))
            txn_str = ', '.join(unique_txns)

        pdf_data = {
            'rows': rows,
            'month': events[0].start.strftime("%b-%Y") if events[0].start else '',
            'employee': events[0].employee,
            'service_order': events[0].project_id.service_order_no_ids.name,
            'total_days': total,
            'abortive_total': total_abortive,
            'approver': events[0].approver.name if events[0].approver else '',
            'txn_str': txn_str,
            'vendor_name': events[0].vendor_id.name if events[0].vendor_id else '',
            'inspector_name': events[0].employee or '',
        }
        res_ids = events.ids if hasattr(events, 'ids') else [e.id for e in events]
        pdf, _ = self.env['ir.actions.report']._render_qweb_pdf(
            'zip_reports.report_timesheet_pdf_turkstream',
            res_ids,
            data=pdf_data
        )

        return pdf

    def _render_group_reports(self, event_ids, is_tcm, report_data, txn_str):
        """Render one group's Excel/PDF pair. Runs in a worker thread, so it
        opens its own cursor/environment instead of reusing self.env - a
        psycopg2 cursor can't be shared across threads. Profiling showed
        ~97% of generate_report_zip's runtime is spent blocked on the
        external wkhtmltopdf subprocess inside generate_report_pdf_tcm, so
        running groups concurrently here cuts wall time roughly by the
        worker count instead of paying ~2.3s per group sequentially.
        """
        with self.pool.cursor() as new_cr:
            new_env = api.Environment(new_cr, self.env.uid, self.env.context)
            events = new_env['calendar.event'].browse(event_ids)
            model = new_env['zip.reports']
            if is_tcm:
                excel_data = model.generate_report_excel_tcm(events, report_data=report_data)
                pdf_data = model.generate_report_pdf_tcm(events, report_data=report_data, txn_str=txn_str)
            else:
                excel_data = model.generate_report_excel_turkstream(events, report_data=report_data)
                pdf_data = model.generate_report_pdf_turkstream(events, report_data=report_data, txn_str=txn_str)
        return excel_data, pdf_data

    def generate_report_zip(self):
        # Build the domain
        client_id = ('code', 'in', ['TCM', 'petrofac'])
        domain = [client_id]
        domain.append('|')
        domain.append(('include_timesheet', '=', True))
        domain.append(('status', '=', 'verified'))
        if self.coordinator_id:
            domain.append(('user_id', '=', self.coordinator_id.id))
        if self.filter_by == 'period':
            if self.date_from and self.date_to:
                domain.append(('start', '>=', self.date_from))
                domain.append(('start', '<=', self.date_to))
        elif self.filter_by == 'month':
            if self.month_data:
                if len(self.month_data) != 7:
                    raise UserError(_("Invalid Date format"))
                month = self.month_data[0:2]
                year = self.month_data[3:7]
                from_date_join = f"{year}-{month}-01"
                fromdate = datetime.strptime(from_date_join, "%Y-%m-%d")
                enddate = fromdate + relativedelta.relativedelta(months=1) - timedelta(days=1)
                domain.append(('start', '>=', str(fromdate.date())))
                domain.append(('start', '<=', str(enddate.date())))
        # Fetch calendar events based on the domain
        calendar_event = self.env['calendar.event'].search(domain, order="start")
        if not calendar_event:
            raise UserError(_("No Record Found"))

        # Group events in a single pass: coordinator -> client -> group key -> events.
        # (Previously this re-scanned the whole `calendar_event` recordset once per
        # coordinator/client pair, which made this O(n * coordinators * clients).)
        client_selection = dict(calendar_event[0]._fields['client_id_new'].selection)
        grouped = {}
        for event in calendar_event:
            coordinator = event.user_id.name
            client = event.client_id_new
            key = (
                event.initiator_id.name if event.initiator_id else event.project_id.name,
                event.employee, event.employee_role.name, event.vendor_id.name
            )
            grouped.setdefault(coordinator, {}).setdefault(client, {}).setdefault(key, []).append(event)

        # Create a zip buffer to store the zipped reports
        zip_buffer = BytesIO()
        written_paths = set()
        # Create the zip file
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # First pass (cheap, sequential): walk the grouping, create every
            # folder entry, and collect a render task per group. The actual
            # Excel/PDF rendering is deferred to a thread pool below since
            # each group's PDF render blocks on an external wkhtmltopdf
            # process for ~2.3s and groups don't depend on each other.
            tasks = []
            for coordinator, client_groups in grouped.items():
                coordinator_folder = coordinator.replace('/', '-')
                if coordinator_folder not in written_paths:
                    zip_file.writestr(coordinator_folder + '/', '')
                    written_paths.add(coordinator_folder)

                for client, key_groups in client_groups.items():
                    client_name = client_selection.get(client, client)
                    client_folder = client_name.replace('/', '-')
                    client_path = os.path.join(coordinator_folder, client_folder)
                    if client_path not in written_paths:
                        zip_file.writestr(client_path + '/', '')
                        written_paths.add(client_path)

                    for (initiator_project, employee, employee_role, vendor), events in key_groups.items():
                        initiator_folder = initiator_project.replace('/', '-')
                        initiator_path = os.path.join(client_path, initiator_folder)
                        if initiator_path not in written_paths:
                            zip_file.writestr(initiator_path + '/', '')
                            written_paths.add(initiator_path)

                        project_folder = events[0].project_id.name.replace('/', '-')
                        project_path = os.path.join(initiator_path, project_folder) if events[0].initiator_id else os.path.join(client_path, project_folder)
                        if project_path not in written_paths:
                            zip_file.writestr(project_path + '/', '')
                            written_paths.add(project_path)

                        # Create blank Excel file
                        unique_txns = list(dict.fromkeys(e.txn for e in events if e.txn))
                        txn_str = ', '.join(unique_txns)
                        safe_vendor = vendor.replace('/', '')
                        if events[0].initiator_id:

                            file_name = "{}-{}-{}-{}-{}-{}.xlsx".format(txn_str, safe_vendor, events[0].v_location.name, employee, employee_role, events[0].initiator_id.name)
                        else:
                            file_name = "{}-{}-{}-{}-{}.xlsx".format(txn_str, safe_vendor, events[0].v_location.name, employee, employee_role)
                        pdf_name = file_name.replace('.xlsx', '.pdf')

                        excel_folder_path = os.path.join(project_path, 'Excel')
                        if excel_folder_path not in written_paths:
                            zip_file.writestr(excel_folder_path + '/', '')
                            written_paths.add(excel_folder_path)
                        pdf_folder_path = os.path.join(project_path, 'PDF')
                        if pdf_folder_path not in written_paths:
                            zip_file.writestr(pdf_folder_path + '/', '')
                            written_paths.add(pdf_folder_path)

                        # Compute the shared report data once and reuse it for both
                        # the Excel and PDF renderers instead of each one re-deriving
                        # it independently.
                        report_data = self._prepare_report_data(events)
                        event_ids = events.ids if hasattr(events, 'ids') else [e.id for e in events]
                        tasks.append({
                            'event_ids': event_ids,
                            'is_tcm': events[0].client_id_new == 'tcm',
                            'report_data': report_data,
                            'txn_str': txn_str,
                            'excel_path': os.path.join(excel_folder_path, file_name),
                            'pdf_path': os.path.join(pdf_folder_path, pdf_name),
                        })

            # Second pass: render every group's Excel/PDF concurrently.
            max_workers = min(8, max(1, len(tasks)))
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                rendered = list(executor.map(
                    lambda t: self._render_group_reports(t['event_ids'], t['is_tcm'], t['report_data'], t['txn_str']),
                    tasks,
                ))

            # Third pass (sequential): ZipFile isn't thread-safe, so the
            # actual writes happen back on the main thread once every
            # group's data is ready.
            for task, (excel_data, pdf_data) in zip(tasks, rendered):
                zip_file.writestr(task['excel_path'], excel_data)
                zip_file.writestr(task['pdf_path'], pdf_data)

        # Save the final zip
        zip_buffer.seek(0)
        file_data = zip_buffer.read()
        file_b64 = base64.b64encode(file_data)
        file_name = self.coordinator_id.name + '.zip'
        self.write({'file': file_b64, 'file_name': file_name})

        # Returning the zip file to the user
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(self.env.ref('zip_reports.zip_reports_view').id, 'form')],
            'res_model': 'zip.reports',
            'target': 'new',
            'context': self._context
        }
