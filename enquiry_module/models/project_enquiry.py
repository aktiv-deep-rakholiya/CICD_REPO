from  odoo import models ,fields ,api ,  _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import timedelta


class ProjectEnquiry(models.Model):

    _name = 'project.enquiry'
    _description = "Project Enquiry"
    _rec_name ='unique_no'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order ='id desc'

    unique_no = fields.Char(string='Unique No', copy=False, readonly=True, index=True, tracking = True, default='New')
    serial_no = fields.Char(string='Serial No', copy=False, readonly=True, default='New')
    calendar_count = fields.Integer('Calendar Count', compute='_compute_calendar_count', copy=False)
    client_id = fields.Many2one('client.master', tracking = True)

    @api.depends('client_id')
    def compute_client_name(self):
        for rec in self:
            if rec.client_id:
                rec.client_name = rec.client_id.client_name
            else:
                rec.client_name = False

    client_name= fields.Selection([
        ('tcm', 'Tecnimont'),
        ('petrofac', 'Petrofac'),
        ('ace', 'ACE Plantech'),
        ('eneico', 'Eneico'),
        ('edif', 'Edif NDE'),
        ('equasrl', 'Equa SRL'),
        ('lindinger', 'Lindinger USA'),
        ('spxflow', 'Dollinger Filtration Limited'),
        ('global', 'Global SCS'),
        ('tecnicas','Tecnicas Reunidas'),
        ('tecton','Tecton'),
        ('arotec','Arotec'),
        ('clatech','Clatech Consulting Co.Ltd'),
        ('sisisrl','SISI SRL'),
        ('stamicarbon','STAMICARBON'),
        ('jkinspection','JK Inspection Engineering co ltd'),
        ('monarch','Monarch Style'),
        ('inspectorunion','Inspectors Union Co.'),
        ('swissapproval','Swiss Approval Team'),
        ('neilbarnett','Neil Barnett Inspection Services'),
        ('applus','Applus Velosi'),
        ('enzone','Enzone'),
        ('bureau','BUREAU Technical Services'),
        ('unitedglobal','United Global'),
        ('teleios','Teleios Spexxa Engg and Cons'),
        ('phbweser','PHB Weserhutte'),
        ('apollo','Apollo Electromechanical Contracting LLC'),
        ('eurture', 'Eurtrue'),
        ('others', 'Others'),

    ], string='Client', tracking = True, compute='compute_client_name')

    country =fields.Many2one('res.country',string='Country',tracking = True)
    enquiry_date = fields.Date(string='Enquiry Date', default=fields.Datetime.now, copy=False, tracking=True)

    @api.constrains('enquiry_date')
    def _check_enquiry_date(self):
        for enquiry in self:
            if enquiry.enquiry_date and enquiry.enquiry_date > fields.Date.today():
                raise ValidationError("The enquiry date should not be in the future.")


    eigl_person_id = fields.Many2one('eigl.person',string='EICM',tracking = True)
    date_of_cv_submission = fields.Date(string='CV Submission Date', tracking = True, copy=False)
    vendor_id=fields.Many2many('res.partner', 'res_partner_enquiry_rel',string='Vendor',tracking = True)
    sub_vendor=fields.Many2many('sub.vendor','subvendor_enquiry_rel',string='Sub Vendor',tracking = True)
    project_id = fields.Many2one('project.project', string='Project', tracking = True)
    proj_code = fields.Char(string="Project Code", readonly=True)
    proj_description = fields.Char(string="Project Description", readonly=True)
    year = fields.Selection(
        selection='years_selection',
        string=" Year",
        default="2024", tracking = True
    )
    employee_role = fields.Many2one('p4.employee.role', string='Role')
    cat_location= fields.Selection([
        ('companyoffice', 'Company Office'),
        ('remote', 'Remote-Agency Tool'),
        ('remote2', 'Remote-Third Parties Tool'),
        ('vendorfacility', 'Vendor Facility/ Loading Unloading Location'),
        ], string='Location', default='vendorfacility', readonly=False, tracking = True)

    category_expenses = fields.Selection([
        ('oncall', 'OnCall'),
        ('resident1', 'Resident1'),
        ('resident2', 'Resident2'),
        ('resident3', 'Resident3'),
        ('resident4', 'Resident4'),
        ('remotemode', 'Remote mode - half day'),
    ], string='JOB Duration', readonly=False, tracking = True)

    services = fields.Selection([
        ('logistics', 'Logistics'),
        ('expediting', 'Expediting & Scheduling'),
        ('inspection', 'Inspection'),
    ], string='Services', readonly=False, tracking = True, copy=True)

    tags = fields.Selection([
        ('fabricated_structures', 'Fabricated structures'),
        ('static_equipment', 'Static Equipment (PV, HE, Reactors, columns, etc.)'),
        ('rotating_equipment', 'Rotating Equipment (Pumps, compressors, turbines, etc.)'),
        ('packages', 'Packages (Skids, HVAC, telecom, etc.)'),
        ('electrical', 'Electrical (Cables, transformers, motors, etc.)'),
        ('instrumentation', 'Instrumentation ( Transmitters, PLC, DCS, ESD, gauges, etc.)'),
        ('valves', 'Valves'),
        ('material', 'Material (Pipes, plates, forgings, castings, etc.)'),
        ('logistics', 'Logistics (loading / unloading)'),
        ('others', 'Others (painting, lab visits, WPS, WPQ, etc.)'),
        ], string='Tags', readonly=False, tracking = True)

    purchase_id = fields.Many2one('purchase.order', string='Purchase Order No', copy=True, tracking=True)
    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High')],string='Priority',tracking = True,copy = False)
    proposed_inspectors = fields.Many2many('inspector.name','proposed_rel','id','prop', tracking = True, copy=False, string='Proposed Inspector')
    approved_inspector = fields.Many2many('inspector.name','proposed_rel1','id','prop',tracking = True, copy=False, string='Approved Inspector')
    ribbon_message = fields.Char('Ribbon message')
    description = fields.Text( string= 'Notes',tracking = True )
    status = fields.Selection([
        ('new', 'New'),
        ('pending', 'Pending'),
        ('won', 'Won'),
        ('hold', 'Hold'),
        ('lost', 'Lost'),
        ('closed', 'Closed'),
        ],default='new', copy=False,tracking=True)

    stage = fields.Selection([
        ('submitforapproval', 'Waiting For Approval'),
        ('approved', 'Approved'),
        ('rejected','Rejected')
        ],default='submitforapproval', copy=False,tracking = True)
    lost_reason = fields.Char(string='Lost Reason')
    is_calendar_event_created = fields.Boolean('calendar event created', default=False, copy=False,tracking = True)
    is_requested = fields.Boolean('Is Requested ?', default=False, copy=False, store=True)
    is_approve_button = fields.Boolean('Is Approve Requested ?', default=False, copy=False)
    approve_button = fields.Boolean('Requested ?', default=False, copy=False)
    tax_id = fields.Many2many('account.tax', string='Taxes',tracking = True)
    after_approve_button =  fields.Boolean('After Approve button', default=False, copy=False)
    field_edit =  fields.Boolean('Field Edit', default=True, copy=False)
    resource_type = fields.Selection([ ('internal', 'Internal Resource'),
                                        ('external', 'External Resource'),],
                        string='Resource Type', readonly=False,  default='internal',tracking = True)
    is_service_agreement_created = fields.Boolean('Service Agreements', default=False, copy=False, store=True)
    rate_list = fields.Selection([
        ('client_rate', 'Client Rate'),
        ('pricelist_rate', 'Pricelist Rate')],
        string="Rate List", default='pricelist_rate',tracking = True)
    is_sequence_created = fields.Boolean('Is Sequence Created ?', default=False, copy=False)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    inspection_coordinator = fields.Many2one('res.users', "Inspection Coordinator", tracking = True,
                                             domain=lambda self: [('groups_id', 'in', self.env.ref('project_management.group_p4_coordinator').id)])
    date_of_cv_submission = fields.Date(string='CV Submission Date', tracking=True, copy=False)
    visit_date = fields.Date(string='Visit Date', tracking=True, copy=False)

    def action_close_cron(self):
        enq=self.env['project.enquiry'].search([])
        for rec in enq:
            if (fields.Date.context_today(self) > rec.enquiry_date + timedelta(days=5)) and not rec.date_of_cv_submission:
                rec.write({'status': 'closed'})

    def _compute_calendar_count(self):
        for rec in self:
            rec.calendar_count = len(self.env['calendar.event'].search([('unique_no', 'in', [rec.id])]))

    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            if rec.project_id:
                rec.tax_id = rec.project_id.tax_id

    def years_selection(self):
        year = 2024
        year_list = []
        while year != 2040:
            year_list.append((str(year), str(year)))
            year += 1
        return year_list

    def action_view_calender(self):
        self.ensure_one()
        events = self.env['calendar.event'].search([('unique_no', 'in', [self.id])])
        if events:
            action = self.sudo().env.ref('calendar.action_calendar_event').read()[0]
            action['views'] =  [(self.env.ref('calendar.view_calendar_event_form').id, 'form')]
            action['res_id'] = events.ids[0]
            return action

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            project_obj = self.env['project.project'].search([('id', '=', vals['project_id'])])
            if vals.get('date_of_cv_submission'):
                vals['status'] = 'pending'
            if vals.get('serial_no', _('New')) == _('New'):
                vals['serial_no'] = (self.env['ir.sequence'].next_by_code('enquiry.sequence') or _('New'))
            client = self.env['client.master'].search([('id', '=', vals['client_id'])])
            country = self.env['res.country'].search([('id', '=', vals['country'])])
            unique_no = client.name[:2] + country.code + str(vals['year'][-2:]) + vals['serial_no']
            vals['unique_no'] = unique_no.upper()
        res = super(ProjectEnquiry, self).create(vals_list)
        return  res

    def write(self,vals):
        if vals.get('date_of_cv_submission'):
            vals['status'] = 'pending'
        if self.stage == 'approved' and self.field_edit:
            sequence_record = self.env['enquiry.sequence'].search([('unique_no', '=', self.id)], limit=1)
            if not sequence_record:
                sequence_record = self.env['enquiry.sequence'].create({'unique_no': self.id, 'sequence': 1, 'name': self.unique_no})
            else:
                sequence_record.sequence += 1

            vals['unique_no'] = f"{sequence_record.name}-A{sequence_record.sequence}"
            vals['is_sequence_created'] = True

        if vals and self.stage == 'approved' and self.status == 'won':
            vals['field_edit'] = False
            vals['is_requested'] = False
        res = super(ProjectEnquiry, self).write(vals)
        return res

    def won_statusbar(self):
        if not self.date_of_cv_submission:
            raise UserError(_("CV Submission Date is Mandatory !"))
        if not self.proposed_inspectors:
            raise UserError(_("Proposed Inspectors is Mandatory !"))
        if not self.approved_inspector:
            raise UserError(_("Approved Inspector is Mandatory !"))
        if not self.inspection_coordinator:
            raise UserError(_("Inspection Coordinator is Mandatory !"))

        ceo_groups = self.env.ref('project_management.group_enquiry_ceo')
        comm_co = self.env.user.partner_id.id
        level1_users = self.env['res.users'].search([('groups_id', 'in', [ceo_groups.id])])
        partner_ids = set()
        if self.env.user.partner_id:
            partner_ids.add(comm_co)
        partner_ids.update(
            user.partner_id.id for user in level1_users if user.partner_id
        )

        partner_ids = list(partner_ids)

        if partner_ids:
            # Send notification using partner_ids instead of notification_ids
            # Create HTML content and sanitize it
            message = self.message_post(
                body='Enquiry Marked as Won!',
                message_type='notification',
            )
            for partner_id in partner_ids:
                self.env['mail.notification'].create({
                    'mail_message_id': message.id,
                    'res_partner_id': partner_id,
                    'notification_type': 'inbox',
                    'is_read': False,
                })
        self.write({
            'status': 'won',
            'field_edit': False,
            'approve_button': True,
        })

    def action_hold(self):
        if self.inspection_coordinator:
            partner_id = self.inspection_coordinator.partner_id.id
            if partner_id:
                # Send notification using partner_ids instead of notification_ids
                # Create HTML content and sanitize it
                message = self.message_post(
                    body='Hi' + ',' +  'Enquiry Marked as Hold !',
                    message_type='notification',
                )

                self.env['mail.notification'].create({
                    'mail_message_id': message.id,
                    'res_partner_id': partner_id,
                    'notification_type': 'inbox',
                    'is_read': False,
                })

            self.write({
                'status': 'hold',
                'field_edit': False,
                'approve_button': True,
            })
        else:
            raise ValidationError("Please select the Inspector Coordinator !")


    def action_set_lost(self ,lost_reason):
        self.message_post(body=('Enquiry Marked as Lost'))
        self.write({
        'status': 'lost',
        'lost_reason': lost_reason
        })

    def reset_to_new(self):
        self.write({'status': 'new',
                    'is_requested': False,
                    'is_approve_button': False,
                    'approve_button': False,
                    'after_approve_button': False,
                    'field_edit': True,
                    'date_of_cv_submission':False,
                    'proposed_inspectors': False,
                    'approved_inspector' : False
                    })

    def edit_statusbar(self):
        level1_groups = self.env.ref('project_management.group_enquiry_ceo')
        level2_group = self.env.ref('project_management.group_p4_manager')
        level1_users = self.env['res.users'].search([('groups_id', 'in', [level1_groups.id, level2_group.id])])
        partner_ids = set()
        partner_ids.update(
            user.partner_id.id for user in level1_users if user.partner_id
        )

        partner_ids = list(partner_ids)

        if partner_ids:
            # Send notification using partner_ids instead of notification_ids
            # Create HTML content and sanitize it
            message = self.message_post(
                body='Enquiry Form Submitted for Editing!',
                message_type='notification',
            )
            for partner_id in partner_ids:
                self.env['mail.notification'].create({
                    'mail_message_id': message.id,
                    'res_partner_id': partner_id,
                    'notification_type': 'inbox',
                    'is_read': False,
                })
        self.write({
            'stage': 'submitforapproval',
            'is_approve_button': True,
            'after_approve_button': True,
            'approve_button': False,
            'is_requested': True,
        })

    def approve_statusbar(self):
        level1_group = self.env.ref('project_management.group_enquiry_ceo')
        level2_group = self.env.ref('project_management.group_p4_manager')
        level3_group = self.env.ref('project_management.group_enquiry_coordinator')
        level1_users = self.env['res.users'].search([('groups_id', 'in', [level1_group.id, level2_group.id, level3_group.id])])
        partner_ids = set()
        partner_ids.update(
            user.partner_id.id for user in level1_users if user.partner_id
        )

        partner_ids = list(partner_ids)

        if partner_ids:
            # Send notification using partner_ids instead of notification_ids
            # Create HTML content and sanitize it
            message = self.message_post(
                body='Hi' + ',' +  'Your Request Accepted ,You can Edit Now !',
                message_type='notification',
            )
            for partner_id in partner_ids:
                self.env['mail.notification'].create({
                    'mail_message_id': message.id,
                    'res_partner_id': partner_id,
                    'notification_type': 'inbox',
                    'is_read': False,
                })

        self.write({
        'stage': 'approved',
        'after_approve_button': False,
        'field_edit':True,
        'approve_button': True,
        })

    def reject_statusbar(self):

        level1_group = self.env.ref('project_management.group_enquiry_ceo')
        level2_group = self.env.ref('project_management.group_p4_manager')
        level3_group = self.env.ref('project_management.group_enquiry_coordinator')
        level1_users = self.env['res.users'].search([('groups_id', 'in', [level1_group.id, level2_group.id, level3_group.id])])
        partner_ids = set()
        partner_ids.update(
            user.partner_id.id for user in level1_users if user.partner_id
        )

        partner_ids = list(partner_ids)

        if partner_ids:
            # Send notification using partner_ids instead of notification_ids
            # Create HTML content and sanitize it
            message = self.message_post(
                body='Sorry' + ',' +  'Your Request was Rejected!',
                message_type='notification',
            )
            for partner_id in partner_ids:
                self.env['mail.notification'].create({
                    'mail_message_id': message.id,
                    'res_partner_id': partner_id,
                    'notification_type': 'inbox',
                    'is_read': False,
                })

        self.write({
        'stage': 'rejected',
        'is_requested': False,
        'approve_button': False,
            'after_approve_button': False,
        })

    @api.onchange('purchase_id')
    def onchange_purchase_id(self):
        for rec in self:
            if rec.purchase_id:
                rec.vendor_id = rec.purchase_id.partner_id

    @api.onchange('date_of_cv_submission')
    def _onchange_date_of_cv_submission(self):
        for enquiry in self:
            if enquiry.date_of_cv_submission and enquiry.date_of_cv_submission < enquiry.enquiry_date:
                raise ValidationError("CV Submission Date cannot be earlier than Enquiry date.")

    @api.onchange('visit_date','date_of_cv_submission')
    def _onchange_visit_date(self):
        for enquiry in self:
            if enquiry.visit_date and enquiry.visit_date <= enquiry.date_of_cv_submission:
                raise ValidationError("Visit Date cannot be earlier than CV Submission date.")

    def action_schedule_meeting(self):
        if self.unique_no:
            many2many_info = ', '.join(record.ins_name for record in self.approved_inspector)

            unique_no = (
                f"{self.unique_no}/"
                f"{many2many_info}/"
                f"{self.vendor_id.name}/"
                f"{self.project_id.name}"
            )
        return {
            'type': 'ir.actions.act_window',
            'name': 'calander',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_unique_no':self.id,
                'default_client_id_new':self.client_name,
                'default_client_id': self.client_id.id,
                'default_commercial_coordinator_id': self.create_uid.id,
                'default_v_location':self.country.id,
                'default_project_id':self.project_id.id,
                'default_eigl_person_id':self.eigl_person_id.id,
                'default_vendor_id':self.vendor_id.ids,
                'default_sub_vendor':self.sub_vendor.ids,
                'default_employee_role':self.employee_role,
                'default_cat_location':self.cat_location,
                'default_category_expenses': self.category_expenses,
                'default_services': self.services,
                'default_purchase_id': self.purchase_id.id,
                'default_tax_id': self.tax_id.ids,
                'default_employee':",".join([approved_inspector.ins_name for approved_inspector in self.approved_inspector]),
                'default_approved_inspector':self.approved_inspector.id,
                'default_name':  unique_no,
                'default_inspection_coordinator':self.inspection_coordinator.id,
                'default_start':self.visit_date,
                'default_stop': self.visit_date
                },
        }

    @api.onchange('proposed_inspectors')
    def onchange_proposed_inspectors(self):
        for rec in self:
            if rec.proposed_inspectors:
                rec.date_of_cv_submission = fields.Date.today()
            return{'domain':{'approved_inspector':[('id','in',rec.proposed_inspectors.ids)]}}
