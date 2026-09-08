# -*- coding:utf-8 -*-
#!/usr/bin/python
# encoding=utf8

from odoo import api, fields, models, _
from xlwt import *
from io import StringIO
import base64
import time
from datetime import datetime, timedelta
import json
from PIL import Image
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil import relativedelta
from odoo.exceptions import UserError
from io import BytesIO



try:
    import xlwt            
except:
    raise osv.except_osv('Warning !','python-xlwt module missing. Please install it.')

class JkInspectionSummaryReport(models.TransientModel):
    _name = "jk.inspection.summary.report"
    _description = "JK Inspection Timesheet Report"
    
    filter_by = fields.Selection([('period', 'Period Range'), ('month', 'Month')], default='period', string="Filter By")
    
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    month_data = fields.Char("Month Data")
    project_id = fields.Many2one('project.project', string="Project")
    vendor_id = fields.Many2one('res.partner', string="Vendor")
    role_id = fields.Many2one('p4.employee.role', string="Role")
    inspector_id = fields.Many2one('inspector.name', string="Inspector")
    service_no = fields.Many2many(related='project_id.service_order_no_ids', string="Service Number")

    
    file = fields.Binary("File", readonly=True)
    file_name = fields.Char("File Name", size=64, readonly=True)

    @api.onchange('month_data')
    def onchange_month_data(self):
        value = self.month_data
        warning_message = False
        if value:
            # Basic format check: MM/YYYY
            if len(value) != 7 or value[2] != '/':
                warning_message = 'Month format should be MM/YYYY'
            else:
                mm, yyyy = value[:2], value[3:]

                # Month validation
                if not (mm.isdigit() and 1 <= int(mm) <= 12):
                    warning_message = 'MM should be 01 to 12'

                # Year validation
                elif not yyyy.isdigit():
                    warning_message = 'YYYY should be a valid year'

        if warning_message:
            self.month_data = False
            return {
                'warning': {
                    'message': warning_message
                }
            }

    def _build_contexts(self, data):
        result = {}
        result['project_id'] = 'project_id' in data['form'] and data['form']['project_id'] or False
        result['vendor_id'] = 'vendor_id' in data['form'] and data['form']['vendor_id'] or False
        result['role_id'] = 'role_id' in data['form'] and data['form']['role_id'] or False
        result['inspector_id'] = 'inspector_id' in data['form'] and data['form']['inspector_id'] or False
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['month_data'] = data['form']['month_data'] or False
        result['filter_by'] = data['form']['filter_by'] or False
        return result



      
    # @api.multi
    def generate_report_excel(self):
        res = {}
        wbk = xlwt.Workbook()

        borders = xlwt.Borders()
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN

        style_header = XFStyle()
        fnt = Font()
        fnt.bold = True
        fnt.height = 8 * 0x14
        style_header.font = fnt
        al1 = Alignment()
        al1.horz = Alignment.HORZ_CENTER
        al1.vert = Alignment.VERT_CENTER
        al1.wrap = True
        pat2 = Pattern()
        style_header.alignment = al1
        style_header.pattern = pat2
        style_header.borders = borders
        
        style_header1 = XFStyle()
        fnt = Font()
        fnt.name = 'Arial'
        fnt.bold = True
        fnt.height = 14*0x14
        style_header1.font = fnt
        al1 = Alignment()
        al1.horz = Alignment.HORZ_CENTER
        al1.vert = Alignment.VERT_CENTER   
        al1.wrap = True      
        pat2 = Pattern()
        pat2.pattern = Pattern.SOLID_PATTERN
        pat2.pattern_fore_colour = Style.colour_map['light_orange']
        style_header1.alignment = al1
        style_header1.pattern = pat2
        style_header1.borders = borders
        
        style_header_new = XFStyle()        
        fnt = Font()
        fnt.bold = True
        fnt.height = 8*0x14
        style_header_new.font = fnt        
        al1 = Alignment()
        al1.horz = Alignment.HORZ_CENTER
        al1.vert = Alignment.VERT_CENTER 
        al1.wrap = True
        pat2 = Pattern()        
        style_header_new.alignment = al1
        style_header_new.pattern = pat2
        style_header_new.borders = borders

        style_header_left1 = XFStyle()
        fnt = Font()
        fnt.name = 'Arial'
        fnt.bold = True
        fnt.height = 10 * 0x14
        style_header_left1.font = fnt
        al1 = Alignment()
        al1.horz = Alignment.HORZ_LEFT
        al1.vert = Alignment.VERT_CENTER
        al1.wrap = True
        pat2 = Pattern()
        pat2.pattern = Pattern.SOLID_PATTERN
        pat2.pattern_fore_colour = Style.colour_map['light_orange']
        style_header_left1.alignment = al1
        style_header_left1.pattern = pat2
        style_header_left1.borders = borders

        style_header_left = XFStyle()
        fnt = Font()
        fnt.name = 'Arial'
        fnt.bold = True
        fnt.height = 10 * 0x14
        style_header_left.font = fnt
        al1 = Alignment()
        al1.horz = Alignment.HORZ_LEFT
        al1.vert = Alignment.VERT_CENTER
        al1.wrap = True
        pat2 = Pattern()
        style_header_left.alignment = al1
        style_header_left.pattern = pat2
        style_header_left.borders = borders
        
        style_header_new_left = XFStyle()        
        fnt = Font()
        fnt.bold = True
        fnt.height = 8*0x14
        style_header_new_left.font = fnt        
        al1 = Alignment()
        al1.horz = Alignment.HORZ_LEFT
        al1.vert = Alignment.VERT_CENTER 
        al1.wrap = True
        pat2 = Pattern()        
        style_header_new_left.alignment = al1
        style_header_new_left.pattern = pat2
        style_header_new_left.borders = borders

        style_header_new_no_line = XFStyle()
        fnt = Font()
        fnt.bold = True
        fnt.height = 8 * 0x14
        style_header_new_left.font = fnt
        al1 = Alignment()
        al1.horz = Alignment.HORZ_LEFT
        al1.vert = Alignment.VERT_CENTER
        al1.wrap = True
        pat2 = Pattern()
        style_header_new_no_line.alignment = al1
        style_header_new_no_line.pattern = pat2
        


        
        style_header_new_right = XFStyle()        
        fnt = Font()
        fnt.bold = True
        fnt.height = 8*0x14
        style_header_new_right.font = fnt        
        al1 = Alignment()
        al1.horz = Alignment.HORZ_RIGHT
        al1.vert = Alignment.VERT_CENTER 
        al1.wrap = True
        pat2 = Pattern()        
        style_header_new_right.alignment = al1
        style_header_new_right.pattern = pat2
        style_header_new_right.borders = borders
        
        style_header2 = XFStyle()        
        fnt = Font()
        fnt.bold = True
        fnt.height = 10*0x14
        style_header2.font = fnt        
        al1 = Alignment()
        al1.horz = Alignment.HORZ_CENTER
        al1.vert = Alignment.VERT_CENTER 
        al1.wrap = True       
        pat2 = Pattern()
        pat2.pattern = Pattern.SOLID_PATTERN
        pat2.pattern_fore_colour = Style.colour_map['pale_blue']
        style_header2.alignment = al1
        style_header2.pattern = pat2
        style_header2.borders = borders
        
        style_header3 = XFStyle()        
        fnt = Font()
        fnt.bold = True
        fnt.height = 8*0x14
        style_header3.font = fnt        
        al1 = Alignment()
        al1.horz = Alignment.HORZ_CENTER
        al1.vert = Alignment.VERT_CENTER   
        al1.wrap = True       
        pat2 = Pattern()        
        style_header3.alignment = al1
        style_header3.pattern = pat2
        style_header3.borders = borders
        
        style_center_align = XFStyle()
        fnt = Font()
        fnt.name = 'Calibri'
        fnt.height = 11*0x14
        al_c = Alignment()
        al_c.horz = Alignment.HORZ_CENTER
        al_c.vert = Alignment.VERT_CENTER
        style_center_align.font = fnt 
        style_center_align.alignment = al_c
        style_center_align.alignment.wrap = 1
        style_center_align.borders = borders

        style_left_align = XFStyle()
        fnt = Font()
        fnt.name = 'Calibri'
        fnt.height = 11 * 0x14
        al_c = Alignment()
        al_c.horz = Alignment.HORZ_LEFT
        al_c.vert = Alignment.VERT_CENTER
        style_left_align.font = fnt
        style_left_align.alignment = al_c
        style_left_align.borders = borders

        style_left_align_color = XFStyle()
        fnt = Font()
        fnt.name = 'Calibri'
        fnt.height = 11 * 0x14
        style_left_align_color.font = fnt
        al1 = Alignment()
        al1.horz = Alignment.HORZ_LEFT
        al1.vert = Alignment.VERT_CENTER
        al1.wrap = True
        pat2 = Pattern()
        pat2.pattern = Pattern.SOLID_PATTERN
        pat2.pattern_fore_colour = Style.colour_map['pale_blue']
        style_left_align_color.alignment = al1
        style_left_align_color.pattern = pat2
        style_left_align_color.borders = borders


        
        style_center_align_wrap = XFStyle()
        fnt = Font()
        fnt.name = 'Calibri'
        fnt.height = 11*0x14
        al_c = Alignment()
        al_c.horz = Alignment.HORZ_CENTER
        al_c.vert = Alignment.VERT_CENTER
        al_c.wrap = True 
        style_center_align_wrap.font = fnt 
        style_center_align_wrap.alignment = al_c
        style_center_align_wrap.borders = borders
        

        
        sheet1 = wbk.add_sheet('Timesheet Report')

        sheet1.col(0).width = 5500
        sheet1.col(1).width = 4000
        sheet1.col(2).width = 4000
        sheet1.col(3).width = 4000
        sheet1.col(4).width = 8000


        sheet1.row(7).height_mismatch = True
        sheet1.row(7).height = 30*20
        sheet1.row(8).height_mismatch = True
        sheet1.row(8).height = 30 * 20
        sheet1.row(9).height_mismatch = True
        sheet1.row(9).height = 30 * 20
        sheet1.row(10).height_mismatch = True
        sheet1.row(10).height = 30 * 20
        sheet1.row(11).height_mismatch = True
        sheet1.row(11).height = 30 * 20
        sheet1.fit_num_pages = 1

        sheet1.header_str = ''
        sheet1.footer_str = ''



        row = 0
        sheet1.write_merge(row, row, 0, 4, '', style_header_new_no_line)
        row = 1
        sheet1.write_merge(row, row, 0, 4, '', style_header_new_no_line)
        row = 2
        sheet1.write_merge(row, row, 0, 4, '', style_header_new_no_line)
        row = 3
        sheet1.write_merge(row, row, 0, 4, '', style_header_new_no_line)
        row = 4
        sheet1.write_merge(row, row, 0, 4, '',style_header_new_no_line)
        row = 5
        sheet1.write_merge(row, row, 0, 4, '', style_header_new_no_line)
        row = 6
        sheet1.write_merge(row, row, 0, 4, '', style_header_new_no_line)



        row = 8

        sheet1.write_merge(row,row, 0,4, 'Project Name : '+self.project_id.name, style_header_left1)




        row = 10

        sheet1.write_merge(row, row, 0, 4, 'Name of the Vendor : '+self.vendor_id.name, style_header_left1)

        row += 1
        sheet1.write(row, 0, 'Inspection Visit Date', style_header2)
        sheet1.write(row, 1, 'Day', style_header2)
        sheet1.write(row, 2, 'No.of Hours', style_header2)
        sheet1.write(row, 3, 'Kms', style_header2)
        sheet1.write(row, 4, 'Report No.', style_header2)



        
        if self.project_id:
            project = ('project_id','=',self.project_id.id)

        else:
            all_project = self.env['project.project'].search([])
            project = ('project_id','=',all_project.ids)
            
        if self.vendor_id:
            vendor = ('vendor_id','=',self.vendor_id.id)
        else:
            all_vendor = self.env['res.partner'].search([('supplier','=',True)])
            vendor = ('vendor_id','=',all_vendor.ids)
            
        if self.role_id:
            role = ('category', '=', self.role_id)
        else:
            all_role = self.env['p4.employee.role'].search([])
            role = ('employee_role','=',all_role.ids)

        if self.inspector_id:
            inspector = ('employee','=',self.inspector_id.ins_name)
        else:
            all_inspector = self.env['hr.employee'].search([])
            inspector = ('employee','=',all_inspector.ids)



        client_id = ('client_id_new','=','jkinspection')
        if self.filter_by == 'period':
            if self.date_from and self.date_to:
                date_compare = ('start','>=',self.date_from)
                date_compare1 = ('start','<=',self.date_to)
                domain = [project,vendor,inspector,date_compare,date_compare1,client_id]
        if self.filter_by == 'month':
            if self.month_data:
                if self.month_data:
                    if not len(self.month_data) == 7:
                        raise UserError(_("Invalid Date format"))
                    month = self.month_data[0:2]
                    year = self.month_data[3:7]
                    from_date_join = str(year) + '-' + str(month) + '-01'
                    fromdate = datetime.strptime(from_date_join, "%Y-%m-%d")
                    enddate = fromdate + relativedelta.relativedelta(months=1) - timedelta(days=1)
                    fromdate = fromdate.date()
                    enddate = enddate.date()
                    date_compare = ('start','>=',str(fromdate))
                    date_compare1 = ('start','<=',str(enddate))
                    domain = [project,vendor,inspector,date_compare,date_compare1,client_id]
        print ("domain",domain )       
        calendar_event = self.env['calendar.event'].search(domain,order="start,hrs,kms")
        if not calendar_event:
            raise UserError(_("No Record Found"))
        
        start_field_dict = {}
        start_values_data = {}
        purchase_new = []
        purchase_new_val = ''
        print ("cccccccccccC",calendar_event)
        for record in calendar_event:
            start_values = {}
            start_values_new = []
            purchase = ''
            if record.purchase_ids:
                purchase = ", ".join([job.name for job in record.purchase_ids])
            if record.vendor_id:
                vendor = ", ".join([job.name for job in record.vendor_id])
                if record.sub_vendor:
                    vendor_sub = ", ".join([job.name for job in record.sub_vendor])
                    vendor = 'Vendor:' + vendor + '\n' + 'Subvendor: ' + vendor_sub
            else:
                vendor = ''
            if record.employee:
                employee = record.employee.name
            else:
                employee = ''

            if record.employee_role:
                employee_role = record.employee_role.name
            else:
                employee_role = ''

            if record.start:
                start_data_format = datetime.strptime(str(record.start),"%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y")
                start = start_data_format
            else:
                start = ''

            if record.extra_hrs:
                extra_hrs_new = record.extra_hrs
            else:
                extra_hrs_new=''

            if record.hrs:
                hrs_new = record.hrs
            else:
                hrs_new=''

            if record.kms:
                kms_new = record.kms
            else:
                kms_new=''

            
            if record.rpt_number:
                number = record.rpt_number
            else:
                number = ''
            

            
            if record.allday:
                allday = True
            else:
                allday = False
            if record.half_day:

                halfday = True
            else:

                halfday = False

            if record.abortive_visit:
                abortive_visit = True

            else:
                abortive_visit = False

            if record.approver:
               approver = record.approver.name
            else:
               approver = ''

            if record.employee.employee_signature:
                signature = record.employee.employee_signature


                imgdata = base64.b64decode(signature)
                filename = 'some_image.png'  # I assume you have a way of picking unique filenames
                with open(filename, 'wb') as f:
                    f.write(imgdata)

                img = Image.open("some_image.png")
                image_parts = img.split()
                r = image_parts[0]
                g = image_parts[1]
                b = image_parts[2]
                img = Image.merge("RGB", (r, g, b))
                fo = BytesIO()
                img.save('imagetoadd1.bmp')
            else:
                signature =''







            if purchase:
                if purchase not in purchase_new:
                    purchase_new.append(purchase)

            start_values['start'] = start
            start_values['purchase'] = purchase
            start_values['vendor'] = vendor
            # start_values['signature_str'] = signature_str
            start_values['number'] = number
            start_values['allday'] = allday
            start_values['abortive_visit'] = abortive_visit
            start_values['extra_hrs_new'] = extra_hrs_new
            start_values['kms_new'] = kms_new
            start_values['hrs_new'] = hrs_new
            start_values['approver'] = approver
            start_values_new.append(start_values)
            start = datetime.strptime(start,'%d-%m-%Y')
            
            print ("print start value before uploading",start_values,start)
            print ("start values newwwwwwwwww",start_values_new)
            print ("start value dataaAAAAA",start_values_data)
            
            if start in start_values_data.keys():
                #start_values_data[
                matched_rec =0
                for rec in start_values_data[start]:
                    print ("reeeeeeeeeeeee",rec)
                    if rec['kms_new'] == start_values['kms_new'] and rec['hrs_new'] == start_values['hrs_new']:
                        rec['number'] = rec['number']+',\n'+str(number)
                        matched_rec += 1
                if matched_rec == 0:
                    start_values_data[start].append(start_values)
            else:
                start_values_data[start] = start_values_new
            
            print ("ssssssssssssssssssssssssS",start_values_data)
            
        total_hrs = 0
        total_abortive=0
        total_extra_hrs = 0
        total_extra_kms = 0
        totol_fullday = 0
        totol_halfday ='-'
        start_values_data_sort = sorted(start_values_data.items())
        for vals in start_values_data_sort:
            end_row = row
            row1 = row
            allday_check = 0
            halfday_check = 0
            totol_fullday += 1
            # if vals[1][0]['halfday'] == True:
                # totol_halfday += 1
            # else:
                # totol_fullday += 1

            for val in vals[1]:

                row += 1
                first_row = row
                start_row = end_row + 1
                row1 += 1



                sheet1.write(row, 0, val['start'], style_center_align)
                if calendar_event[0]:
                    if calendar_event[0].start:
                        calendar_start_day = datetime.strptime(val['start'], "%d-%m-%Y").strftime(
                            "%A")
                    else:
                        calendar_start_day = ''
                    sheet1.write(row, 1, calendar_start_day, style_center_align_wrap)
                else:
                    sheet1.write(row, 1, '', style_header1)

                if val['abortive_visit'] == False:

                    sheet1.write_merge(row, row, 2, 2, val['hrs_new'], style_center_align)
                    total_hrs += 1
                elif val['abortive_visit'] == True:

                    sheet1.write_merge(row, row, 2, 2, 'Abortive', style_center_align)
                    total_abortive += 1
                else:
                    sheet1.write_merge(row, row, 2, 2, '', style_center_align)
                sheet1.write(row, 3, val['kms_new'], style_center_align_wrap)
                sheet1.write(row, 4, val['number'], style_center_align)





            end_row = row1
            
            # if halfday_check == 1:
                # sheet1.write_merge(start_row, end_row, 8, 8, 1.0, style_center_align)
            # else:
                # sheet1.write_merge(start_row, end_row, 7, 7, 1.0, style_center_align)
            #sheet1.write_merge(start_row, end_row, 7, 7, 1.0, style_center_align)
            #sheet1.write_merge(start_row, end_row, 4, 4,val['start'], style_center_align)

        next_row1 = end_row + 1
        sheet1.write(next_row1, 0, '', style_header)
        sheet1.write(next_row1, 1, '', style_header)
        sheet1.write(next_row1, 2, '', style_header)
        sheet1.write(next_row1, 3, '', style_header)
        sheet1.write(next_row1, 4, '', style_left_align)



        next_row = next_row1 + 1
        sheet1.write_merge(next_row, next_row, 0, 1, 'No of Full Days Worked', style_header_left)
        sheet1.write_merge(next_row, next_row, 2, 4, str(total_hrs), style_header_left)


            


        next1_row = next_row + 1
        sheet1.write_merge(next1_row, next1_row, 0, 1, 'No of Abortive Days', style_header_left)
        sheet1.write_merge(next1_row, next1_row, 2, 4, str(total_abortive), style_header_left)

        next12_row = next1_row + 1
        sheet1.write_merge(next12_row, next12_row, 0, 4, '')




        next2_row = next12_row + 1
        sheet1.row(next2_row).height_mismatch = True
        sheet1.row(next2_row).height = 50 * 20


        sheet1.write_merge(next2_row, next2_row, 0, 1, 'Name of Inspector : '+self.inspector_id.name, style_header_left)
        if record.employee.employee_signature:
            sheet1.write_merge(next2_row, next2_row, 2, 4, 'Signature:', style_header_left)

            sheet1.insert_bitmap('imagetoadd1.bmp', next2_row, 3, 4 , scale_x=0.9, scale_y=.2 ,y=2.5 )
        else:
            sheet1.write_merge(next2_row, next2_row, 2, 4, 'Signature:', style_header_left)


        next13_row = next2_row + 1
        sheet1.write_merge(next13_row, next13_row, 0, 4, '')

        next3_row = next13_row + 1
        sheet1.row(next3_row).height_mismatch = True
        sheet1.row(next3_row).height = 50 * 20

        sheet1.write_merge(next3_row,next3_row, 0,1, 'Name of Approving Authority :'+val['approver'], style_header_left)
        sheet1.write_merge(next3_row,next3_row, 2,4, 'Signature:', style_header_left)



        row = 7
        if calendar_event[0]:
            if calendar_event[0].start:
                calendar_start_date = datetime.strptime(calendar_event[0].start,"%Y-%m-%d %H:%M:%S").strftime("%b-%Y")
            else:
                calendar_start_date = ''
            sheet1.write_merge(row,row,0, 4, 'Summary of Timesheet - '+calendar_start_date, style_header1)
        else:
            sheet1.write(4, 4, '', style_header1)
        #for val in set(purchase_new):
            #print len(set(purchase_new)), "len"
            #print len(set(purchase_new))/2

        row = 9

        name =""
        for val in record.purchase_id_multi :

              name += str(val.name)+','
        if len(purchase_new) > 0:
            po_numbers = ','.join(purchase_new)
        else:
            po_numbers = ''
        sheet1.write_merge(row, row, 0, 4,'PO Number : '+ po_numbers, style_header_left1)




        string = ""
        for i, purchase in enumerate(set(purchase_new)):
            if i == 0:
                string += purchase
            elif i%2 != 0 and i != 0:
                string += ", " + purchase
            else:
                string += ", \n" + purchase
            
            #purchase_new_val += str(val)+',\n'



        file_data=BytesIO()
        # byme
        # file_data=StringIO.StringIO()
        o=wbk.save(file_data)
        """string encode of data in wksheet"""
        out=base64.encodestring(file_data.getvalue())
        """returning the output xls as binary"""
        file_f = out
        filename = 'Timesheet Report'
        
        self.write({'file':out, 'file_name':filename})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'res_model': 'jk.inspection.summary.report',
            'target': 'new',
            'context': self._context
            }

# class Reportvisitsummary(models.AbstractModel):
    # _name = 'report.prime4_report.report_visit_summary'
    
    # def _lines(self, data, partner):
        # full_account = []
        # if data['form']['project_id']:
            # project = ('project_id','=',data['form']['project_id'][0])
        # else:
            # all_project = self.env['project.project'].search([])
            # project = ('project_id','=',all_project.ids)
            
        # if data['form']['vendor_id']:
            # vendor = ('vendor_id','=',data['form']['vendor_id'][0])
        # else:
            # all_vendor = self.env['res.partner'].search([('supplier','=',True)])
            # vendor = ('vendor_id','=',all_vendor.ids)
            
        # if data['form']['role_id']:
            # role = ('employee_role','=',data['form']['role_id'][0])
        # else:
            # all_role = self.env['p4.employee.role'].search([])
            # role = ('employee_role','=',all_role.ids)
            
        # if data['form']['inspector_id']:
            # inspector = ('employee','=',data['form']['inspector_id'][0])
        # else:
            # all_inspector = self.env['hr.employee'].search([])
            # inspector = ('employee','=',all_inspector.ids)
                   
        # if data['form']['filter_by']  == 'period':
            # if data['form']['date_from'] and data['form']['date_to']:
                # date_compare = ('start','>=',data['form']['date_from'])
                # date_compare1 = ('start','<=',data['form']['date_to'])
                # domain = [project,vendor,role,inspector,date_compare,date_compare1]
                # calendar_event = self.env['calendar.event'].search(domain,order="start")
        # if data['form']['filter_by'] == 'month':
            # if data['form']['month_data']:
                # month = data['form']['month_data'][0:2]
                # year = data['form']['month_data'][3:7]
                # from_date_join = str(year) + '-' + str(month) + '-01'
                # fromdate = datetime.strptime(from_date_join, "%Y-%m-%d")
                # enddate = fromdate + relativedelta.relativedelta(months=1) - timedelta(days=1)
                # fromdate = fromdate.date()
                # enddate = enddate.date()
                # date_compare = ('start','>=',str(fromdate))
                # date_compare1 = ('start','<=',str(enddate))
                # domain = [project,vendor,role,inspector,date_compare,date_compare1]
                # calendar_event = self.env['calendar.event'].search(domain,order="start")
        
        # if not calendar_event:
            # raise UserError(_("No Record Found"))
        
        # start_field_dict = {}
        # start_values_data = {}
        # purchase_new = []
        # purchase_new_val = ''
        # for record in calendar_event:
            # start_values = {}
            # start_values_new = []
            # purchase = ''
            # if record.purchase_id:
                # purchase = record.purchase_id.name
            # if record.vendor_id:
                # vendor = record.vendor_id.name
                # if record.sub_vendor:
                    # vendor_sub = record.sub_vendor.name
                    # vendor = vendor + ' - ' + vendor_sub
            # else:
                # vendor = ''
            # if record.employee:
                # employee = record.employee.name
            # else:
                # employee = ''

            # if record.employee_role:
                # employee_role = record.employee_role.name
            # else:
                # employee_role = ''
            
            # if record.start:
                # start_data_format = datetime.strptime(str(record.start),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                # start = start_data_format
            # else:
                # start = ''
            
            # if record.rpt_number:
                # number = record.rpt_number
            # else:
                # number = ''
            
            # if record.eigl_person_id:
                # eigl_person = record.eigl_person_id.name
            # else:
                # eigl_person = ''

            # if record.half_day:
                # allday = False
                # halfday = True
            # else:
                # allday = True
                # halfday = False

            # if purchase:
                # purchase_new.append(purchase)    

            # start_values['purchase'] = purchase
            # start_values['vendor'] = vendor
            # start_values['employee'] = employee
            # start_values['employee_role'] = employee_role
            # start_values['start'] = start
            # start_values['number'] = number
            # start_values['eigl_person'] = eigl_person
            # start_values['allday'] = allday
            # start_values['halfday'] = halfday
            # start_values_new.append(start_values)
            # start = datetime.strptime(start,"%d/%m/%Y")
            # if start in start_values_data.keys():
                # start_values_data[start].append(start_values)
            # else:
                # start_values_data[start] = start_values_new
        # start_values_data_new = sorted(start_values_data.items())
        
        # country_name = ''
        # contract = ''
        # data_project = ''
        # calendar_start_date = ''
        # if calendar_event[0]:
            # if calendar_event[0].start:
                # calendar_start_date = datetime.strptime(calendar_event[0].start,"%Y-%m-%d %H:%M:%S").strftime("%b-%Y")
            # else:
                # calendar_start_date = ''
            # for val in set(purchase_new):
                # purchase_new_val += str(val)+',\n'
            # data_project = 'Project No - '+ str(calendar_event[0].project_id.project_id)+'; PO# ' + str(purchase_new_val)
            # country_name = calendar_event[0].v_location.name
            # if calendar_event[0].employee_role.name == 'Inspector':
                # contract = calendar_event[0].project_id.inspection_contract_no
            # if calendar_event[0].employee_role.name == 'Expeditor':
                # contract = calendar_event[0].project_id.expediting_contract_no
            # #contract = calendar_event[0].employee.contract_id.name
            
        # totol_fullday = 0
        # totol_halfday = 0
        # for vals in start_values_data_new:
            # if vals[1][0]['halfday'] == True:
                # totol_halfday += 1
            # else:
                # totol_fullday += 1
        # totol_fullday = str(totol_fullday) + '.0'
        # totol_halfday = str(totol_halfday) + '.0'
        # return [start_values_data_new,data_project,country_name,calendar_start_date,contract,totol_fullday,totol_halfday]

    # @api.model
    # def render_html(self, docids, data=None):
        # docargs = {
            # 'data': data,
            # 'lines': self._lines,
        # }
        # return self.env['report'].render('prime4_report.report_visit_summary', docargs)
