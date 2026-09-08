# -*- coding:utf-8 -*-
#!/usr/bin/python
# encoding=utf8

from odoo import api, fields, models, _
from xlwt import *
from io import StringIO, BytesIO
import base64
import time
from datetime import datetime, timedelta
import json
from PIL import Image  
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil import relativedelta
from odoo.exceptions import UserError

try:
    import xlwt            
except:
    raise osv.except_osv('Warning !','python-xlwt module missing. Please install it.')

class StamicarbonSummaryReport(models.TransientModel):
    _name = "stamicarbon.summary.report"
    _description = "Timesheet Report"
    
    filter_by = fields.Selection([('period', 'Period Range'), ('month', 'Month')], default='period', string="Filter By")
    
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    month_data = fields.Char("Month Data")
    project_id = fields.Many2one('project.project', string="Project")
    vendor_id = fields.Many2one('res.partner', string="Vendor")
    role_id = fields.Many2one('p4.employee.role', string="Role")
    inspector_id = fields.Many2one('inspector.name', string="Inspector")
    
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
    def generate_report_pdf(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'month_data', 'filter_by', 'project_id', 'vendor_id', 'role_id', 'inspector_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        return self.env['report'].get_action(self, 'prime4_report.report_visit_summary', data=data)
      
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
        fnt.height = 8*0x14
        style_header.font = fnt        
        al1 = Alignment()
        al1.horz = Alignment.HORZ_CENTER
        al1.vert = Alignment.VERT_CENTER   
        al1.wrap = True      
        pat2 = Pattern()        
        style_header.alignment = al1
        style_header.pattern = pat2
        style_header.borders = borders
        
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
        fnt.height = 8*0x14
        style_header2.font = fnt        
        al1 = Alignment()
        al1.horz = Alignment.HORZ_CENTER
        al1.vert = Alignment.VERT_CENTER 
        al1.wrap = True       
        pat2 = Pattern()
        pat2.pattern = Pattern.SOLID_PATTERN
        pat2.pattern_fore_colour = Style.colour_map['ivory']  
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
        fnt.height = 8*0x14
        al_c = Alignment()
        al_c.horz = Alignment.HORZ_CENTER
        al_c.vert = Alignment.VERT_CENTER
        style_center_align.font = fnt 
        style_center_align.alignment = al_c
        style_center_align.borders = borders
        
        style_center_align_wrap = XFStyle()
        fnt = Font()
        fnt.height = 8*0x14
        al_c = Alignment()
        al_c.horz = Alignment.HORZ_CENTER
        al_c.vert = Alignment.VERT_CENTER
        al_c.wrap = True 
        style_center_align_wrap.font = fnt 
        style_center_align_wrap.alignment = al_c
        style_center_align_wrap.borders = borders
        
        style_left_align = XFStyle()
        al_l = Alignment()
        al_l.horz = Alignment.HORZ_LEFT
        al_l.vert = Alignment.VERT_CENTER
        style_left_align.alignment = al_l  
        style_left_align.borders = borders
        
        sheet1 = wbk.add_sheet('Timesheet Report')
        sheet1.col(0).width = 2800
        sheet1.col(1).width = 7500
        sheet1.col(2).width = 4200
        sheet1.col(3).width = 2000
        sheet1.col(4).width = 2400
        sheet1.col(5).width = 5200
        sheet1.col(6).width = 4400
        sheet1.col(7).width = 1100
        sheet1.col(8).width = 1100
        sheet1.col(9).width = 2300
        sheet1.col(10).width = 2750
        
        sheet1.row(10).height = 500
           
        company = self.env['res.company'].search([])[0]
        image = self.env.user.company_id.logo
        
        row = 0
        # byme
        # file_image = open('c:\prime4\images\logo.png', 'wb')
        # file_image.write(image.decode('base64'))
        # file_image.close()
        
        # Image.open('c:\prime4\images\logo.png').convert("RGB").save('logo.bmp') 
           
        # sheet1.insert_bitmap('logo.bmp',0,0,scale_x = .7, scale_y = .5)
        row = 3
        sheet1.write(row, 4, 'Contract', style_header)
        sheet1.write(row, 5, '', style_header)
        # if self.role_id.name.lower() == 'inspector':
        #     if self.project_id.inspection_contract_no:
        #         sheet1.write(row, 5, self.project_id.inspection_contract_no, style_header2)
        #     else:
        #         sheet1.write(row, 5, '', style_header2)
        # elif self.role_id.name.lower() == 'expeditor':
        #     if self.project_id.expediting_contract_no:
        #         sheet1.write(row, 5, self.project_id.expediting_contract_no, style_header2)
        #     else:
        #         sheet1.write(row, 5, '', style_header2)
        # else:
        #     if self.project_id.inspection_contract_no:
        #         sheet1.write(row, 5, self.project_id.inspection_contract_no, style_header2)
        #     else:
        #         sheet1.write(row, 5, '', style_header2)
        # elif self.role_id.name.lower() == 'specialist inspector':
            # if self.project_id.expediting_contract_no:
                # sheet1.write(row, 5, self.project_id.inspection_contract_no, style_header2)
            # else:
                # sheet1.write(row, 5, '', style_header2)

        # else:
            # sheet1.write(row, 5, '', style_header2)
        sheet1.write_merge(row, row, 7, 8, 'Month', style_header_new_left)
        row = 4
        sheet1.write(row, 0, 'Agency', style_header_new)
        sheet1.write(row, 1, company.name, style_header2)
        sheet1.write_merge(row, row, 7, 8, 'Country', style_header_new_left)
        row = 5
        
        row += 1    
        sheet1.write(row, 0, 'P.O. Nr.', style_header)
        sheet1.write(row, 1, 'VENDOR/PORT', style_header)
        sheet1.write(row, 2, 'INSPECTOR', style_header)
        sheet1.write(row, 3, 'ROLE', style_header)
        sheet1.write(row, 4, 'VISIT DATE', style_header)
        sheet1.write(row, 5, 'REPORT NUMBER', style_header)
        sheet1.write(row, 6, 'EICM', style_header)
        sheet1.write_merge(row, row, 7, 8, '', style_header2)
        sheet1.write(row, 9, 'Expenses \nEUR', style_header)
        sheet1.write(row, 10, 'Expenses \nDescription', style_header)
        
        row += 1
        sheet1.write(row, 0, '', style_header)
        sheet1.write(row, 1, '', style_header)
        sheet1.write(row, 2, '', style_header)
        sheet1.write(row, 3, '', style_header)
        sheet1.write(row, 4, '', style_header)
        sheet1.write(row, 5, '', style_header)
        sheet1.write(row, 6, '', style_header)
        sheet1.write(row, 7, 'OD', style_header2)
        sheet1.write(row, 8, 'HD', style_header2)
        sheet1.write(row, 9, '', style_header)
        sheet1.write(row, 10, '', style_header)
        
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
        
        if self.filter_by == 'period':
            if self.date_from and self.date_to:
                date_compare = ('start','>=',self.date_from)
                date_compare1 = ('start','<=',self.date_to)
                domain = [project,vendor,role,inspector,date_compare,date_compare1]
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
                    domain = [project,vendor,role,inspector,date_compare,date_compare1]
                
        calendar_event = self.env['calendar.event'].search(domain,order="start")
        if not calendar_event:
            raise UserError(_("No Record Found"))
        
        start_field_dict = {}
        start_values_data = {}
        purchase_new = []
        purchase_new_val = ''
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
                start_data_format = datetime.strptime(str(record.start),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                start = start_data_format
            else:
                start = ''
            
            if record.rpt_number:
                number = record.rpt_number
            else:
                number = ''
            
            if record.eigl_person_id:
                eigl_person = record.eigl_person_id.name
            else:
                eigl_person = ''
            
            #if record.allday:
                #allday = True
                #halfday = False
            if record.half_day:
                allday = False
                halfday = True
            else:
                allday = True
                halfday = False  

            if purchase:
                purchase_new.append(purchase)    

            start_values['purchase'] = purchase
            start_values['vendor'] = vendor
            start_values['employee'] = employee
            start_values['employee_role'] = employee_role
            start_values['start'] = start
            start_values['number'] = number
            start_values['eigl_person'] = eigl_person
            start_values['allday'] = allday
            start_values['halfday'] = '-'
            start_values_new.append(start_values)
            start = datetime.strptime(start,"%d/%m/%Y")
            if start in start_values_data.keys():
                start_values_data[start].append(start_values)
            else:
                start_values_data[start] = start_values_new
         
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
                sheet1.write(row, 0, val['purchase'], style_center_align_wrap)
                sheet1.write(row, 1, val['vendor'], style_center_align_wrap)
                sheet1.write(row, 2, val['employee'], style_center_align)
                sheet1.write(row, 3, val['employee_role'], style_center_align)
                sheet1.write(row, 5, val['number'], style_center_align)
                sheet1.write(row, 6, val['eigl_person'], style_center_align)
                sheet1.write(row, 8, '-', style_center_align)
                #if val['halfday'] == True:
                # if vals[1][0]['halfday'] == True:
                    # sheet1.write(row, 7, '-', style_center_align)
                    # halfday_check = 1
                # else:
                    # sheet1.write(row, 8, '-', style_center_align)
                
                sheet1.write(row, 9, '-', style_center_align)
                sheet1.write(row, 10, '-', style_center_align)
            end_row = row1
            
            # if halfday_check == 1:
                # sheet1.write_merge(start_row, end_row, 8, 8, 1.0, style_center_align)
            # else:
                # sheet1.write_merge(start_row, end_row, 7, 7, 1.0, style_center_align)
            sheet1.write_merge(start_row, end_row, 7, 7, 1.0, style_center_align)
            sheet1.write_merge(start_row, end_row, 4, 4,val['start'], style_center_align)
            
        next_row = end_row + 1
        sheet1.write(next_row, 0, '', style_header)
        sheet1.write(next_row, 1, '', style_header)
        sheet1.write(next_row, 2, '', style_header)
        sheet1.write(next_row, 3, '', style_header)
        sheet1.write(next_row, 4, '', style_header)
        sheet1.write(next_row, 5, '', style_header)
        sheet1.write(next_row, 6, '', style_header)
        
        sheet1.write(next_row, 7, str(totol_fullday), style_center_align)
        sheet1.write(next_row, 8, str(totol_halfday), style_center_align)
            
        sheet1.write(next_row, 9, '', style_header)
        sheet1.write(next_row, 10, '', style_header)

        if calendar_event[0]:
            if calendar_event[0].start:
                # calendar_start_date = datetime.strptime(calendar_event[0].start,"%Y-%m-%d %H:%M:%S").strftime("%b-%Y")
                print(type(calendar_event[0].start), calendar_event[0].start)
                calendar_start_date = calendar_event[0].start.strftime("%b-%Y")
            else:
                calendar_start_date = ''
            sheet1.write(3, 6, calendar_start_date, style_header_new_right)
        else:
            sheet1.write(3, 6, '', style_header_new_right)
        #for val in set(purchase_new):
            #print len(set(purchase_new)), "len"
            #print len(set(purchase_new))/2
        
        string = ""
        for i, purchase in enumerate(set(purchase_new)):
            if i == 0:
                string += purchase
            elif i%2 != 0 and i != 0:
                string += ", " + purchase
            else:
                string += ", \n" + purchase
            
            #purchase_new_val += str(val)+',\n'

        data_project = str(self.project_id.project_id)+'; PO# ' + str(string)
        sheet1.write(4, 4, 'Project', style_header_new)
        sheet1.write(4, 5, data_project, style_header_new)
        sheet1.write(4, 6, calendar_event[0].v_location.name, style_header_new_right)

        file_data=BytesIO()
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
            'res_model': 'stamicarbon.summary.report',
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
