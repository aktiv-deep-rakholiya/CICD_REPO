# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError,ValidationError
from odoo.tools import html_sanitize
from lxml import etree



class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def attachment_tree_view(self):
        self.ensure_one()
        domain = ['&', ('res_model', '=', 'calendar.event'), ('res_id', 'in', self.ids)]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'list,form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the Timesheet</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to your Timesheet.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for calendar in self:
            calendar.doc_count = Attachment.search_count(['&',('res_model', '=', 'calendar.event'), ('res_id', '=', calendar.id)])

    def button_submit(self):
        for rec in self:
            # If direct submission, skip review flow
            if rec.is_direct:
                rec.status = 'verified'
                continue
            if not rec.inspection_coordinator == self.env.user:
                raise ValidationError(
                    _("This event belongs to %s, so you cannot submit it for review", rec.inspection_coordinator.name))
            rec.write({'status': 'review'})
            if not rec.reviewer_id:
                raise UserError(_("Before Submitting specify the Reviewer "))
            if rec.reviewer_id:
                level1_group = self.env.ref('project_management.group_enquiry_ceo')
                level2_users = self.env['res.users'].search([('groups_id', 'in', [level1_group.id])])
                level1_users = self.env['res.users'].search([('id', '=', rec.reviewer_id.id)])
                # Collect all partner IDs to notify
                partner_ids = set()
                # Add reviewer partner
                if level1_users.partner_id:
                    partner_ids.add(level1_users.partner_id.id)
                # Add level2_users partners
                partner_ids.update(
                    user.partner_id.id for user in level2_users if user.partner_id
                )
                partner_ids = list(partner_ids)
                if partner_ids:
                    # Send notification using partner_ids instead of notification_ids
                    # Create HTML content and sanitize it
                    html_body = html_sanitize('Hi ' + str(self.reviewer_id.name) + ', ' +
                                              'Please review this ' +
                                              '<a href="/web#id=' + str(
                        rec.id) + '&model=calendar.event&view_type=form">' +
                                              str(rec.name) + '</a>. Thanks.',
                                              sanitize_tags=False, strip_classes=True)
                    message=self.message_post(
                        body=html_body,
                        message_type='notification',
                    )
                    for partner_id in partner_ids:
                        self.env['mail.notification'].create({
                            'mail_message_id': message.id,
                            'res_partner_id': partner_id,
                            'notification_type': 'inbox',
                            'is_read': False,
                        })

    def button_verify(self):
        for rec in self:
            if not rec.reviewer_id == self.env.user:
                raise ValidationError(_("This event belongs to %s, so you cannot submit it for Approval",
                                        rec.reviewer_id.name))
            if (rec.status == 'review' and not self.env.user.has_group(
                    'project_management.group_p4_reviewer')) and not self.env.user.has_group('base.group_system'):
                raise UserError(_("You Cannot Modifiy the Calendar !!!"))
            rec.write({'status': 'submit'})

        if self.approver_id and self.rpt_number:
            level1_group = self.env.ref('project_management.group_enquiry_ceo')
            level2_users = self.env['res.users'].search([('groups_id', 'in', [level1_group.id])])
            level1_users = self.env['res.users'].search([('id', '=', self.approver_id.id)])
            # Collect all partner IDs to notify
            partner_ids = set()
            # Add approver partner
            if level1_users.partner_id:
                partner_ids.add(level1_users.partner_id.id)
            # Add level2_users partners
            partner_ids.update(
                user.partner_id.id for user in level2_users if user.partner_id
            )
            partner_ids = list(partner_ids)

            if partner_ids:
                # Send notification using partner_ids instead of notification_ids
                # Create HTML content and sanitize it
                html_body = html_sanitize('Hi ' + str(self.approver_id.name) + ', ' +
                                          '<a href="/web#id=' + str(
                    self.id) + '&model=calendar.event&view_type=form">' +
                                          str(self.name) + '</a> reviewed successfully. Please proceed with approval. Thanks.',
                                          sanitize_tags=False, strip_classes=True)
                message = self.message_post(
                    body=html_body,
                    message_type='notification',
                )
                for partner_id in partner_ids:
                    self.env['mail.notification'].create({
                        'mail_message_id': message.id,
                        'res_partner_id': partner_id,
                        'notification_type': 'inbox',
                        'is_read': False,
                    })

        if not self.approver_id:
            raise UserError(_("Before Verifying specify the approver name"))

    def button_approve(self):
        not_submit = self.filtered(lambda r: r.status != 'submit')
        if not_submit:
            names = ', '.join(not_submit.mapped('name'))
            raise ValidationError(_("Cannot approve these records because they are not in submit state: %s") % names)

        for rec in self:
            approver = rec.approver_id
            user = self.env.user

            # Check if user is allowed
            if not (user == approver or
                    user.has_group('project_management.group_enquiry_ceo') or
                    user.has_group('base.group_system')):
                raise UserError(_("You cannot perform this action for record %s!" % rec.name))

            # Only allow approver to approve
            if rec.approver_id != user:
                raise ValidationError(_("This event belongs to %s, so you cannot Approve it" % rec.approver_id.name))

            # Approve the record
            rec.write({'status': 'verified'})

            # Notify relevant partners
            level1_group = self.env.ref('project_management.group_enquiry_ceo')
            level2_users = self.env['res.users'].search([('groups_id', 'in', [level1_group.id])])
            level1_users = self.env['res.users'].browse(rec.inspection_coordinator.id)

            partner_ids = set()
            if level1_users.partner_id:
                partner_ids.add(level1_users.partner_id.id)
            partner_ids.update(user.partner_id.id for user in level2_users if user.partner_id)
            partner_ids = list(partner_ids)

            if partner_ids:
                html_body = html_sanitize(
                    f'Hi, <a href="/web#id={rec.id}&model=calendar.event&view_type=form">{rec.name}</a> '
                    f'Approved successfully for report number '
                    f'<a href="/web#id={rec.id}&model=calendar.event&view_type=form">{rec.rpt_number}</a>. Thanks.',
                    sanitize_tags=False, strip_classes=True
                )
                message = rec.message_post(
                    body=html_body,
                    message_type='notification',
                )
                for partner_id in partner_ids:
                    self.env['mail.notification'].create({
                        'mail_message_id': message.id,
                        'res_partner_id': partner_id,
                        'notification_type': 'inbox',
                        'is_read': False,
                    })

    def button_approve_ins(self):
        for rec in self:
            rec.write({'status': 'verified'})
        admin_group = self.env.ref('base.group_system')
        admin_users = self.env['res.users'].search([('groups_id', '=', admin_group.id)])
        partner_ids = set()
        partner_ids.update(
            user.partner_id.id for user in admin_users if user.partner_id
        )
        partner_ids = list(partner_ids)
        if partner_ids:
            html_body = html_sanitize('Hi, ' +
                                      '<a href="/web#id=' + str(
                self.id) + '&model=calendar.event&view_type=form">' +
                                      str(self.name) + '</a> Resubmited for report number ' +
                                      '<a href="/web#id=' + str(
                self.id) + '&model=calendar.event&view_type=form">' +
                                      str(self.rpt_number) + '</a>. Thanks.',
                                      sanitize_tags=False, strip_classes=True)
            message = self.message_post(
                body=html_body,
                subject="Requested",
                message_type='notification',
            )
            for partner_id in partner_ids:
                self.env['mail.notification'].create({
                    'mail_message_id': message.id,
                    'res_partner_id': partner_id,
                    'notification_type': 'inbox',
                    'is_read': False,
                })

    def button_reject(self):
        approver = self.env['res.users'].browse(self.approver_id.id)
        if (self.env.user == approver or self.env.user.has_group(
                'project_management.group_enquiry_ceo') or self.env.user.has_group('base.group_system')):
            for rec in self:
                if not rec.approver_id == self.env.user:
                    raise ValidationError(_("This event belongs to %s, so you cannot Reject it",
                                            rec.approver_id.name))
                rec.write({'status': 'review'})
            level1_group = self.env.ref('project_management.group_enquiry_ceo')
            level2_users = self.env['res.users'].search([('groups_id', 'in', [level1_group.id])])
            level1_users = self.env['res.users'].search([('id', '=', self.inspection_coordinator.id)])
            # Collect all partner IDs to notify
            partner_ids = set()
            # Add inspection_coordinator partner
            if level1_users.partner_id:
                partner_ids.add(level1_users.partner_id.id)
            # Add level2_users partners
            partner_ids.update(
                user.partner_id.id for user in level2_users if user.partner_id
            )
            partner_ids = list(partner_ids)
            if partner_ids:
                # Send notification using partner_ids instead of notification_ids
                # Create HTML content and sanitize it
                html_body = html_sanitize('Hi, ' +
                                          '<a href="/web#id=' + str(
                    self.id) + '&model=calendar.event&view_type=form">' +
                                          str(self.name) + '</a> is rejected.',
                                          sanitize_tags=False, strip_classes=True)
                message = self.message_post(
                    body=html_body,
                    message_type='notification',
                )
                for partner_id in partner_ids:
                    self.env['mail.notification'].create({
                        'mail_message_id': message.id,
                        'res_partner_id': partner_id,
                        'notification_type': 'inbox',
                        'is_read': False,
                    })
        else:
            raise UserError(_("You cannot perform this action"))

    def button_coordinator_submit(self):
        if str(self.reviewer_id.name) != 'DIRECT':
            raise UserError(_("Please check reviewer name is DIRECT"))
        return self.write({'status': 'submit'})

    def action_edit(self):
        return self.write({'status': 'edit'})
    
    def button_reopen(self):
        for rec in self:
            rec.write({'status': 'open'})
    

    @api.model
    def get_views(self, views, options=None):
        result = super().get_views(views, options=options)
 
        is_reviewer = self.env.user.has_group(
            'project_management.group_p4_reviewer'
        )
        is_coordinator = self.env.user.has_group(
            'project_management.group_p4_coordinator'
        )
        is_commercial_coordinator = self.env.user.has_group(
            'project_management.group_enquiry_coordinator'
        )
 
        if not (is_reviewer and not (is_coordinator or is_commercial_coordinator)):
            return result
 
        editable_fields = {
            'notification_no',
            'rpt_number',
            'approver_id',
            'description',
            'recurrence_update',
        }
 
        for view_type, view_data in result['views'].items():
            if view_type != 'form':
                continue
 
            arch = view_data.get('arch')
            if arch is None:
                continue
 
            # arch in get_views is a string, so parse it first
            tree = etree.fromstring(arch.encode())
 
            for node in tree.xpath("//field"):
                if node.get('name') not in editable_fields:
                    node.set('readonly', '1')
                elif 'readonly' in node.attrib:
                    del node.attrib['readonly']
 
            # Convert back to string
            view_data['arch'] = etree.tostring(tree, encoding='unicode')
 
        return result


    client_id = fields.Many2one('client.master', tracking=True, store=True)

    @api.depends('client_id')
    def compute_client_name(self):
        for rec in self:
            if rec.client_id:
                rec.client_id_new = rec.client_id.client_name
            else:
                rec.client_id_new = False

    client_id_new = fields.Selection([
        ('tcm', 'Tecnimont'),
        ('petrofac', 'Petrofac'),
        ('ace', 'ACE Plantech'),
        ('eneico', 'Eneico'),
        ('edif', 'Edif NDE'),
        ('equasrl', 'Equa SRL'),
        ('lindinger', 'Lindinger USA'),
        ('spxflow', 'Dollinger Filtration Limited'),
        ('global', 'Global SCS'),
        ('tecnicas', 'Tecnicas Reunidas'),
        ('tecton', 'Tecton'),
        ('arotec', 'Arotec'),
        ('clatech', 'Clatech Consulting Co.Ltd'),
        ('sisisrl', 'SISI SRL'),
        ('stamicarbon', 'STAMICARBON'),
        ('jkinspection', 'JK Inspection Engineering co ltd'),
        ('monarch', 'Monarch Style'),
        ('inspectorunion', 'Inspectors Union Co.'),
        ('swissapproval', 'Swiss Approval Team'),
        ('neilbarnett', 'Neil Barnett Inspection Services'),
        ('applus', 'Applus Velosi'),
        ('enzone', 'Enzone'),
        ('bureau', 'BUREAU Technical Services'),
        ('unitedglobal', 'United Global'),
        ('teleios', 'Teleios Spexxa Engg and Cons'),
        ('phbweser', 'PHB Weserhutte'),
        ('apollo', 'Apollo Electromechanical Contracting LLC'),
        ('eurture', 'Eurtrue'),
        ('others', 'Others'),
    ], string='Client', default='tcm', compute='compute_client_name')
    inspection_coordinator = fields.Many2one('res.users', "Inspection Coordinator", tracking=True,
                                             domain=lambda self: [('groups_id', 'in', self.env.ref(
                                                 'project_management.group_p4_coordinator').id)])

    cat_location = fields.Selection([
        ('companyoffice', 'Company Office'),
        ('remote', 'Remote-Agency Tool'),
        ('remote2', 'Remote-Third Parties Tool'),
        ('vendorfacility', 'Vendor Facility/ Loading Unloading Location'),
    ], string='Location', default='vendorfacility', readonly=False)

    category_expenses = fields.Selection([
        ('oncall', 'OnCall'),
        ('resident1', 'Resident1'),
        ('resident2', 'Resident2'),
        ('resident3', 'Resident3'),
        ('resident4', 'Resident4'),
        ('remotemode', 'Remote mode - half day'),
    ], string='JOB Duration', readonly=False)

    services = fields.Selection([
        ('logistics', 'Logistics'),
        ('expediting', 'Expediting & Scheduling'),
        ('inspection', 'Inspection'),
    ], string='Services', readonly=False, copy=False)
    vendor_id = fields.Many2many('res.partner', 'partner_calendar_rel', string='Vendor', tracking = True)
    purchase_id = fields.Many2one('purchase.order',
                                    string='Purchase Order', store=True, tracking=True)
    project_id = fields.Many2one('project.project', string='Project', tracking=True)
    task_id = fields.Many2one('project.task', string='Task')
    v_location = fields.Many2one('res.country', string='Country', tracking=True)
    eigl_person_id = fields.Many2one('eigl.person', string='EIGL', tracking=True)
    sub_vendor = fields.Many2many('sub.vendor','subvenor_calendar_rel',string='Sub Vendor',tracking = True)
    half_day = fields.Boolean(string='Half Day', default=False)
    allday = fields.Boolean('All Day', default=True)
    rpt_number = fields.Char(string='Report Number', tracking=True)
    provisional = fields.Boolean('Provisional', tracking=True)
    is_direct = fields.Boolean('Direct Review/Approve', tracking=True)
    include_timesheet = fields.Boolean('Include Pending Timesheet')

    @api.onchange('provisional')
    def _onchange_provisional(self):
        self.rpt_number = False
        if self.provisional:
            self.rpt_number = "PROVISIONAL"

    proj_state = fields.Selection([
        ('planned', 'Planned'),
        ('pending', 'Pending'),
        ('reviewwaiting', 'Review Waiting'),
        ('submitted', 'Submitted to client'),
    ], string='Report Status', default='planned')
    employee=fields.Char(string='Approved Inspector')
    approved_inspector = fields.Many2one('inspector.name', string='Approved Inspector')

    @api.onchange('approved_inspector')
    def _approved_inspector(self):
        for rec in self:
            rec.employee = rec.approved_inspector.ins_name

    status = fields.Selection([
        ('open', 'Open'),
        ('review', 'Submitted for Review'),
        ('submit', 'Submitted for Approval'),
        ('verified', 'Approved'),
        ('edit', 'Reopen'),
    ], string='Status', default='open', tracking=True, copy=False)

    recurrence_update_persisted = fields.Selection(
        selection=[
            ('self_only', "This event"),
            ('future_events', "This and following events"),
            ('all_events', "All events"),
        ], copy=False,
    )

    recurrence_update = fields.Selection(
        selection=[
            ('self_only', "This event"),
            ('future_events', "This and following events"),
            ('all_events', "All events"),
        ], store=False, copy=False, readonly=False,
        compute='_compute_recurrence_update_default',
        help="Choose what to do with other events in the recurrence. "
             "Updating All Events is not allowed when dates or time is modified",
    )

    @api.depends('recurrency', 'recurrence_update_persisted')
    def _compute_recurrence_update_default(self):
        for rec in self:
            rec.recurrence_update = rec.recurrence_update_persisted or 'future_events'

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached",
                               tracking=True)
    reviewer_id = fields.Many2one('res.users', "Reviewer", tracking=True,
                                  domain=lambda self: [
                                      ("groups_id", "=", self.env.ref("project_management.group_p4_reviewer").id)])
    approver_id = fields.Many2one('res.users', "Approver", tracking=True,
                                  domain=lambda self: [('groups_id', 'in',
                                                        [self.env.ref('project_management.group_p4_manager').id,
                                                         self.env.ref('project_management.group_enquiry_ceo').id])])
    state = fields.Selection([('draft', 'Unconfirmed'), ('open', 'Confirmed')], string='State', readonly=True,
                             tracking=True, default='draft')
    employee_role = fields.Many2one('p4.employee.role', string='Role')
    agency_id_name = fields.Many2one('agency.number', string='Agency')
    travel_hrs = fields.Integer('Travel Hours')
    client_of_client_id = fields.Many2one('client.client', string="Client's Client")
    report_hrs = fields.Integer('Report Hours')
    last_message = fields.Text('Latest Message')
    misc_expen = fields.Text('Miscellaneous Expenses')
    event_status = fields.Selection([
        ('createcalanderevent', 'Create Calendar Event'),
        ('submitforapproval', 'Submit for Approval'),
        ('approved', 'Approved'),
    ], default='createcalanderevent', copy=False)
    overnight_expense = fields.Boolean(string="With Overnight Expense")
    compute_field = fields.Boolean(string="check field")
    with_stay = fields.Boolean(string="With Stay", compute="get_stay_field")
    commercial_coordinator_id = fields.Many2one('res.users', copy=False, store=True, tracking=True)
    without_stay = fields.Boolean(string="Without Stay", compute="get_stay_field")
    is_worked_on_holiday_sunday = fields.Boolean(string="Worked on Holiday/Sunday", default=False)
    is_worked_on_extended_hours = fields.Boolean(string="Worked on Extended Hours", default=False)
    skip_man_day = fields.Boolean(string='Skip Man day in Report/Billing', default=False, groups='project_management.group_skip_man_day')

    def read(self, fields=None, load='_classic_read'):
        if fields and 'skip_man_day' in fields and not self.env.user.has_group(
                'project_management.group_skip_man_day'):
            return self.sudo().read(fields, load)
        return super().read(fields=fields, load=load)

    def check_field_access_rights(self, operation, field_names):
        if (operation == 'read' and field_names
                and 'skip_man_day' in field_names
                and not self.env.user.has_group(
                    'project_management.group_skip_man_day')):
            return super(CalendarEvent, self.sudo()).check_field_access_rights(
                operation, field_names
            )
        return super().check_field_access_rights(operation, field_names)

    @api.depends('overnight_expense')
    def get_stay_field(self):
        for rec in self:
            rec.with_stay = rec.overnight_expense
            rec.without_stay = not rec.with_stay

    @api.onchange('with_stay')
    def _stay(self):
        if self.with_stay:
            self.without_stay = False

    @api.onchange('purchase_id')
    def onchange_purchase_id(self):
        for rec in self:
            if rec.purchase_id:
                rec.vendor_id = rec.purchase_id.partner_id

    @api.onchange('without_stay')
    def _stay_1(self):
        if self.without_stay:
            self.with_stay = False

    @api.onchange('inspection_coordinator', 'reviewer_id', 'approver_id')
    def onchange_coordinator(self):
        partner_ids = []
        for record in [self.inspection_coordinator, self.reviewer_id, self.approver_id, self.commercial_coordinator_id]:
            if record and record.partner_id:
                partner_ids += record.partner_id.ids
        self.partner_ids = [(6, 0, partner_ids)]

    @api.model
    def _get_recurrence_non_propagating_fields(self):
        """Fields excluded from non-destructive propagation to following events
        in the same recurrence. Time and recurrence fields are excluded because
        each event has its own slot in the series; identity/system fields are
        excluded because they would either be wrong to copy or would re-trigger
        recurrence machinery."""
        exclude = set(self._get_time_fields()) | self._get_recurrent_fields()
        exclude |= {
            'id', 'active',
            'recurrence_id', 'follow_recurrence', 'recurrency',
            'attendee_ids', 'access_token',
            'create_date', 'create_uid', 'write_date', 'write_uid',
            'recurrence_update', 'recurrence_update_persisted',
            'allday', 'duration',
        }
        return exclude

    @api.onchange('recurrence_update')
    def _onchange_recurrence_update(self):
        for rec in self:
            if rec.recurrency and rec.recurrence_update:
                rec.recurrence_update_persisted = rec.recurrence_update

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_worked_on_holiday_sunday') and vals.get('is_worked_on_extended_hours'):
                raise ValidationError(_(
                    "A visit cannot be both 'Worked on Holiday/Sunday' and 'Worked on Extended Hours' at the same time. Please select only one."
                ))
        return super().create(vals_list)

    def write(self, values):
        for rec in self:
            holiday = values.get('is_worked_on_holiday_sunday', rec.is_worked_on_holiday_sunday)
            extended = values.get('is_worked_on_extended_hours', rec.is_worked_on_extended_hours)
            if holiday and extended:
                raise ValidationError(_(
                    "A visit cannot be both 'Worked on Holiday/Sunday' and 'Worked on Extended Hours' at the same time. Please select only one."
                ))
        # When a single recurring event is being edited and the change isn't a
        # recursive propagation from this method itself, honour the radio
        # selection (recurrence_update) and write the same propagating values
        # to the appropriate subset of events in the recurrence — without
        # rebuilding the recurrence (which would archive/recreate events and
        # lose work).
        propagate_to = self.env['calendar.event']
        propagating_values = {}
        is_propagation = self.env.context.get('_recurrence_propagation')
 
        # 'button_recurrence_update' is supplied by buttons that need to honour
        # the current radio value from the form (the field itself isn't
        # reliable at button time — it's computed and resets to the default).
        button_choice = self.env.context.get('button_recurrence_update')
 
        is_recurrence_structure_change = bool(self._get_recurrent_fields() & values.keys())

        # Unchecking "Recurrent" on a single occurrence triggers base's
        # _compute_recurrence (it depends on 'recurrency'), which resets all
        # RRULE proxy fields (interval, rrule_type, byday, ...) to False as a
        # side effect — the user isn't editing the recurrence rule, just
        # detaching this occurrence. Left in values, that noise would trip
        # the "self_only can't change the rule" guard below, so strip it and
        # let only 'recurrency' itself be written on this event.
        if (not is_propagation
                and len(self) == 1
                and self.recurrence_id
                and values.get('recurrency') is False):
            for field in self._get_recurrent_fields():
                values.pop(field, None)
            values.pop('recurrence_update', None)
            is_recurrence_structure_change = False

        if (not is_propagation
                and len(self) == 1
                and self.recurrence_id
                and is_recurrence_structure_change
                and self.status in ('open', 'edit')):
            # Let base write() handle this: it knows how to rewrite/rebuild
            # the recurrence for 'all_events'/'future_events'. Restore
            # recurrence_update instead of consuming it, otherwise base
            # always sees None and rejects the change outright.
            recurrence_setting = (
                values.get('recurrence_update')
                or button_choice
                or self.recurrence_update_persisted
                or 'future_events'
            )
            if recurrence_setting == 'self_only':
                # A recurrence rule (Repeat/Until/...) applies to the whole
                # series and can't be scoped to "This event" only. Instead of
                # blocking the save, drop the rule-field changes and write
                # everything else normally on this event alone.
                for field in self._get_recurrent_fields():
                    values.pop(field, None)
                values.pop('recurrence_update', None)
                values['recurrence_update_persisted'] = recurrence_setting
            else:
                values['recurrence_update'] = recurrence_setting
                values['recurrence_update_persisted'] = recurrence_setting
        elif (not is_propagation
                and len(self) == 1
                and self.recurrence_id):
            recurrence_setting = (
                values.pop('recurrence_update', None)
                or button_choice
                or values.get('recurrence_update_persisted')  # set by _onchange_recurrence_update
                or self.recurrence_update_persisted            # existing DB value
                or 'future_events'                            # first-time default only
            )
 
            # Persist the user's pick so the radio still shows it after the
            # save reloads the form (the transient `recurrence_update` field
            # would otherwise reset to its default on reload).
            values['recurrence_update_persisted'] = recurrence_setting
 
            non_propagating = self._get_recurrence_non_propagating_fields()
            propagating_values = {
                k: v for k, v in values.items() if k not in non_propagating
            }
 
            if recurrence_setting == 'all_events':
                propagate_to = self.recurrence_id.calendar_event_ids.filtered(
                    lambda e: e.id != self.id and e.active
                )
            elif recurrence_setting == 'future_events':
                propagate_to = self.recurrence_id.calendar_event_ids.filtered(
                    lambda e: e.id != self.id and e.active and e.start >= self.start
                )
            # else 'self_only': leave propagate_to empty so only the current
            # event is written below.
        else:
            # Always strip recurrence_update so we never trigger the standard
            # destructive rebuild — propagation is handled here.
            values.pop('recurrence_update', None)
 
        result = super().write(values)
 
        if propagating_values and propagate_to:
            propagate_to.with_context(
                _recurrence_propagation=True,
            ).write(propagating_values)
 
        return result