from odoo import models ,fields, api, _
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.exceptions import UserError


class TimesheetReport(models.TransientModel):
    _name = "timesheet.report"
    _description = "Timesheet Report"
    _order = "id desc"

    filter_by = fields.Selection([('period', 'Period Range'), ('month', 'Month')], default='month', string="Filter By")
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    month_data = fields.Char("Month Data")
    project_id = fields.Many2one('project.project', string="Project")
    inspector_idd = fields.Many2one('inspector.name', string="Inspector")
    client_id = fields.Many2one('client.master', string="Client")

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

    def submit_btn(self):
        status = ('status', '=', 'verified')
        project = ('project_id', '=', self.project_id.id)
        client = ('client_id', '=', self.client_id.id)
        inspector = ('employee', '=', self.inspector_idd.ins_name)
        if self.filter_by == 'period':
            if self.date_from and self.date_to:
                date_compare = ('start', '>=', self.date_from)
                date_compare1 = ('start', '<=', self.date_to)
                domain = [date_compare, date_compare1, status]
                if self.project_id:
                    domain.append(project)
                if self.inspector_idd:
                    domain.append(inspector)
                if self.client_id:
                    domain.append(client)

                from_format = self.date_from.strftime("%d/%m/%Y")
                to_format = self.date_to.strftime("%d/%m/%Y")
                fromdate = self.date_from
                todate = self.date_to

        if self.filter_by == 'month':
            if self.month_data:
                month = self.month_data[0:2]
                year = self.month_data[3:7]
                from_date_join = str(year) + '-' + str(month) + '-01'
                fromdate = datetime.strptime(from_date_join, "%Y-%m-%d")
                enddate = fromdate + relativedelta.relativedelta(months=1) - timedelta(days=1)
                fromdate = fromdate.date()
                todate = enddate.date()
                enddate = enddate.date()
                date_compare = ('start', '>=', str(fromdate))
                date_compare1 = ('start', '<=', str(enddate))
                domain = [date_compare, date_compare1, status]
                if self.project_id:
                    domain.append(project)
                if self.client_id:
                    domain.append(client)
                if self.inspector_idd:
                    domain.append(inspector)

        calendar_event = self.env['calendar.event'].search(domain)

        if not calendar_event:
            raise UserError(_("No Record Found"))

        summary = self.env['summary.report'].search([('date_from', '>=', fromdate),('date_to', '<=', todate),
                                                     ('project_id', '=', self.project_id.id)])

        if summary and not (self.env.user.has_group('project_management.accounts_role') or self.env.user.has_group(
                'base.group_system')):
            raise UserError(_("Timesheet Already Generated"))
        else:
            project_ids = []
            for rec in calendar_event:
                if rec and not rec in self.env['summary.report'].search([]).mapped('emp_list').mapped('calendar_ids'):
                    summary_exists = self.env['summary.report'].search(
                        [('date_from', '>=', fromdate),('date_to', '<=', todate),('project_id', '=', rec.project_id.id), ('approve', '=', False),
                         ('not_approve', '=', False)])
                    if summary_exists and (summary_exists.approve == False and summary_exists.not_approve == False):
                        emp_exists = self.env['emp.list'].search([('emp_name', '=', rec.employee),
                                                                  ('country', '=', rec.v_location.id),
                                                                  ('category_expenses', '=', rec.category_expenses),
                                                                  ('services', '=', rec.services),
                                                                  ('cat_location', '=', rec.cat_location),
                                                                  ('employee_role', '=', rec.employee_role.id),
                                                                  ('client_id', '=', rec.client_id.id),
                                                                  ('with_stay', '=', rec.with_stay),
                                                                  ('without_stay', '=', rec.without_stay),
                                                                  ], limit=1, order='id desc')
                        if emp_exists:
                            if not rec in emp_exists.calendar_ids:
                                emp_exists.write({'days': emp_exists.days + rec.total_days,
                                                  'add_expenses': emp_exists.add_expenses + rec.add_expenses_rtpcr1 +
                                                                  rec.add_expenses_mileage1 + rec.add_expenses_airfare1,
                                                  'calendar_ids': emp_exists.calendar_ids.ids + rec.ids,
                                                  'partner_ids': emp_exists.partner_ids.ids + rec.vendor_id.ids,
                                                  'tax_id': emp_exists.tax_id.ids + rec.client_id.tax_ids.ids,
                                                  'purchase_id': rec.purchase_id.id,
                                                  })
                        else:
                            summary_exists.write({'emp_list': [(0, 0, {
                                "country": rec.v_location.id,
                                "employee_role": rec.employee_role.id,
                                "cat_location": rec.cat_location,
                                "category_expenses": rec.category_expenses,
                                "services": rec.services,
                                "emp_name": rec.employee,
                                "days": rec.total_days,
                                "add_expenses": rec.add_expenses_rtpcr1 + rec.add_expenses_mileage1 + rec.add_expenses_airfare1,
                                "client_name": rec.client_id_new,
                                "client_id": rec.client_id.id,
                                "with_stay": rec.with_stay,
                                "overnight_expense":rec.overnight_expense,
                                "without_stay": rec.without_stay,
                                "calendar_ids": rec.ids,
                                "partner_ids": rec.vendor_id.ids,
                                "purchase_id": rec.purchase_id.id,
                                "tax_id": rec.client_id.tax_ids.ids,
                            })]})

                    else:
                        vals = {
                            'project_id': rec.project_id.id,
                            "purchase_id": rec.purchase_id.id,
                            "client_name": rec.client_id_new,
                            "street": rec.street,
                            "street2": rec.street2,
                            "zip": rec.zip,
                            "city": rec.city,
                            "state_id": rec.state_id.id,
                            "country_id": rec.country_id.id,
                            "price_list": rec.price_list.id,
                            "pay_term": rec.pay_term.id,
                            "currency": rec.currency.id,
                            "vat_code": rec.vat_code,
                            "tel_num": rec.tel_num,
                            "fax": rec.fax,
                            "attn": rec.attn,
                            "trn": rec.trn,
                            "purchase_date": rec.purchase_date,
                            "month_data": self.month_data if self.month_data else str(from_format) + '-' + str(to_format),
                            "date": fromdate,
                            "date_from": fromdate,
                            "date_to": todate,
                        }

                        vals["emp_list"] = [(0, 0, {
                            "country": rec.v_location.id,
                            "employee_role": rec.employee_role.id,
                            "cat_location": rec.cat_location,
                            "category_expenses": rec.category_expenses,
                            "services": rec.services,
                            "emp_name": rec.employee,
                            "days": rec.total_days,
                            "add_expenses": rec.add_expenses_rtpcr1 + rec.add_expenses_mileage1 + rec.add_expenses_airfare1,
                            "client_name": rec.client_id_new,
                            "client_id": rec.client_id.id,
                            "with_stay": rec.with_stay,
                            "overnight_expense":rec.overnight_expense,
                            "without_stay": rec.without_stay,
                            "calendar_ids": rec.ids,
                            "partner_ids": rec.vendor_id.ids,
                            "purchase_id": rec.purchase_id.id,
                            "tax_id": rec.client_id.tax_ids.ids
                        })]

                        self.env['summary.report'].create(vals)
                    project_ids.append(rec.project_id.id)
                continue
            if not project_ids:
                line_domain = []
                summary_ids = self.env['summary.report'].search([('project_id', '=', self.project_id.id),
                                                                 ('date_from', '>=', fromdate),('date_to', '<=', todate)])
                if summary_ids:
                    line_domain = [('emp_id', 'in', summary_ids.ids)]
                if self.inspector_idd:
                    line_domain += [('emp_name', '=', self.inspector_idd.ins_name)]
                if self.client_id:
                    line_domain += [('client_id', '=', self.client_id.id)]
                summary_lines = self.env['emp.list'].search(line_domain)

                emp = self.env['summary.report'].search([('id', 'in', summary_lines.emp_id.ids)])
                if emp:
                    raise UserError(_("Timesheet Already Generated %s") % (", ".join([job.name for job in emp])))

            if project_ids:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Timesheet Report',
                    'res_model': 'summary.report',
                    'domain': [('project_id', 'in', list(set(project_ids))), ('date', '=', fromdate)],
                    'view_mode': 'list,form',
                }
