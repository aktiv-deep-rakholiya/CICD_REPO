from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import html_sanitize


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'
    _order ="create_date desc"

    unique_no = fields.Many2one('project.enquiry', string='Unique No', tracking=True)
    jar = fields.Boolean('JAR', default=False)
    email = fields.Boolean('EMail', default=False)
    code = fields.Char(related='client_id.code', store=True, copy=False)
    km = fields.Char(default='Kms',  store=True, copy=False)

    @api.depends('stop_date')
    def _compute_total_days(self):
        for record in self:
            if record.start_date and record.stop_date:
                total_days = (record.stop_date - record.start_date).days + 1
                record.total_days = max(total_days, 0)
            else:
                record.total_days = 0

    currency_id = fields.Many2one(related='client_id.currency_id', store=True, copy=False)
    jar_email = fields.Selection([
        ('jar', 'JAR'),
        ('email', 'EMail'),
    ],  string='Jar/Email')

    date = fields.Date('Date', default = fields.Datetime.now)
    jar_email_date = fields.Date('Jar/Email Date')
    add_day_travel = fields.Boolean('Additional Day Travel', default=False)

    add_expenses_rtpcr = fields.Boolean('Additional Hotel stay', default=False)
    add_expenses_rtpcr1 = fields.Float(string="Additional Hotel stay", digits=(6, 3), store=True)

    add_expenses_airfare = fields.Boolean('Additional Travel expenses', default=False)
    add_expenses_airfare1 = fields.Float(string="Additional Travel expenses", digits=(6, 3), store=True)

    add_expenses_mileage = fields.Boolean('Additional Expenses Mileage', default=False)
    add_expenses_mileage1 = fields.Float(string="Additional Expenses Mileage", default = 0, digits=(6, 3), store=True)
    add_km_mileage1 = fields.Float(string="Additional Expenses Mileage", default=0, digits=(6, 2), store=True)

    @api.onchange('allday')
    def onchange_all_day(self):
        if self.allday:
            self.half_day = False
        else:
            self.half_day = True

    @api.onchange('half_day')
    def onchange_half_day(self):
        if self.half_day:
            self.allday = False
        else:
            self.allday = True

    @api.onchange('add_km_mileage1')
    def _additional_mileage(self):
        self.add_expenses_mileage1 = self.add_km_mileage1 * 0.50

    total_days = fields.Integer('No of Days' ,default=0, compute = '_compute_total_days')
    event_state = fields.Selection([
        ('submitforapproval', 'Waiting For Approval'),
        ('approved', 'Approve'),
        ('rejected','Reject')
        ],default='submitforapproval', copy = False)

    tax_id = fields.Many2many('account.tax', string='Taxes')

    # for invoice
    street = fields.Char('Street', readonly=False)
    street2 = fields.Char('Street2', readonly=False)
    zip = fields.Char('Zip',readonly=False)
    city = fields.Char('City', readonly=False)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        readonly=False, store=True)
    price_list = fields.Many2one(
        'product.pricelist', string='Pricelist')

    pay_term = fields.Many2one(
        'account.payment.term', string='Payment Terms')
    currency = fields.Many2one('res.currency', string="Currency")

    vat_code = fields.Char(string="Vat Code", index=True, tracking=True)
    tel_num = fields.Char(string="Tel Num", index=True, tracking=True)
    fax = fields.Char(string="Fax", index=True, tracking=True)
    attn = fields.Char(string="Attn", index=True, tracking=True)
    trn = fields.Char(string="TRN", index=True, tracking=True)
    purchase_date = fields.Date(string='Purchase Date')
    resource_type = fields.Selection([('internal', 'Internal Resource'),
                                      ('external', 'External Resource'), ],
                                     string='Resource Type', readonly=False, copy=False)

    rate_list = fields.Selection([
        ('client_rate', 'Client Rate'),
        ('pricelist_rate', 'Pricelist Rate')],
        string="Rate List", default='client_rate', copy = False)
    serial_no = fields.Char(string='Serial No', translate=True, copy=True, readonly=True, index=True)
    name = fields.Char('Meeting Subject', required=True, store=True, compute="_compute_name",readonly=False)

    @api.depends('unique_no','txn','employee','vendor_id','project_id')
    def _compute_name(self):
        for rec in self:
            base = rec.unique_no.unique_no if rec.unique_no and rec.unique_no.unique_no else rec.txn
            parts = [base] if base else []

            if rec.employee:
                parts.append(rec.employee)

            if rec.vendor_id:
                parts.append(rec.vendor_id.name)

            if rec.project_id and rec.project_id.name:
                parts.append(rec.project_id.name)

            rec.name = "/".join(parts)

    @api.onchange('purchase_id')
    def onchange_purchase_id(self):
        for rec in self:
            if rec.purchase_id:
                rec.purchase_date = rec.purchase_id.purchase_date
                rec.vendor_id = rec.purchase_id.partner_id
            else:
                rec.vendor_id = False

    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            if rec.project_id:
                rec.street = rec.project_id.street
                rec.street2 = rec.project_id.street2
                rec.zip = rec.project_id.zip
                rec.city = rec.project_id.city
                rec.state_id = rec.project_id.state_id.id
                rec.country_id = rec.project_id.country_id.id
                rec.price_list = rec.project_id.price_list
                rec.pay_term = rec.project_id.pay_term
                rec.currency = rec.project_id.currency
                rec.vat_code = rec.project_id.vat_code
                rec.tel_num = rec.project_id.tel_num
                rec.fax = rec.project_id.fax
                rec.attn = rec.project_id.attn
                rec.trn = rec.project_id.trn

    @api.onchange('unique_no')
    def onchange_unique_no(self):
        for rec in self:
            if rec.unique_no:
                event = self.env['calendar.event'].search([('unique_no','=', rec.unique_no.id)])
                if event:
                    raise UserError(_("Calendar Event Already Created !: %s")%(event.name))
                rec.project_id = rec.unique_no.project_id
                rec.client_id_new = rec.unique_no.client_name
                rec.client_id = rec.unique_no.client_id.id
                rec.eigl_person_id = rec.unique_no.eigl_person_id
                rec.employee_role = rec.unique_no.employee_role
                rec.commercial_coordinator_id  =  rec.unique_no.create_uid.id
                rec.cat_location = rec.unique_no.cat_location
                rec.category_expenses = rec.unique_no.category_expenses
                rec.services = rec.unique_no.services
                rec.vendor_id = rec.unique_no.vendor_id.ids
                rec.sub_vendor = rec.unique_no.sub_vendor.ids
                rec.tax_id = rec.unique_no.tax_id.ids
                rec.resource_type = rec.unique_no.resource_type
                rec.rate_list = rec.unique_no.rate_list
                rec.serial_no = rec.unique_no.serial_no
                rec.inspection_coordinator = rec.unique_no.inspection_coordinator.id
                rec.employee = ",".join(
                    [approved_inspector.ins_name for approved_inspector in rec.unique_no.approved_inspector])
                rec.v_location = rec.unique_no.country
                rec.purchase_id = rec.unique_no.purchase_id.id
                rec.description = rec.unique_no.description
            else:
                rec.unique_no.is_calendar_event_created = False

    def approve_statusbar1(self):
        partner_id = self.inspection_coordinator.partner_id.id
        if partner_id:
            # Send notification using partner_ids instead of notification_ids
            # Create HTML content and sanitize it
            message = self.message_post(
                body='Hi ' +str(self.inspection_coordinator.name) + ',' +  'You can Edit Now !',
                message_type='notification',
            )

            self.env['mail.notification'].create({
                'mail_message_id': message.id,
                'res_partner_id': partner_id,
                'notification_type': 'inbox',
                'is_read': False,
            })
        self.write({
        'event_status': 'approved',
        'event_state': 'approved',
        })

    def calendar_event_create_notification(self):
        level1_groups = self.env.ref('project_management.group_enquiry_ceo')
        level1_users = self.env['res.users'].search([('groups_id', 'in', [level1_groups.id])])

        partner_ids = set()

        if self.inspection_coordinator and self.inspection_coordinator.partner_id:
            partner_ids.add(self.inspection_coordinator.partner_id.id)

        partner_ids.update(
            user.partner_id.id for user in level1_users if user.partner_id
        )
        partner_ids = list(partner_ids)
        if partner_ids:
            # Send notification using partner_ids instead of notification_ids
            # Create HTML content and sanitize it
            message = self.message_post(
                body='Calendar Event Created !',
                message_type='notification',
            )
            for partner_id in partner_ids:
                self.env['mail.notification'].create({
                    'mail_message_id': message.id,
                    'res_partner_id': partner_id,
                    'notification_type': 'inbox',
                    'is_read': False,
                })


    def action_submit(self):

        level1_group = self.env.ref('project_management.group_enquiry_ceo')
        level1_users = self.env['res.users'].search([('groups_id', 'in', [level1_group.id])])
        partner_ids = set()
        if self.approver_id and self.approver_id.partner_id:
            partner_ids.add(self.approver_id.partner_id.id)
        partner_ids.update(
            user.partner_id.id for user in level1_users if user.partner_id
        )
        partner_ids = list(partner_ids)

        if partner_ids:
            # Send notification using partner_ids instead of notification_ids
            # Create HTML content and sanitize it
            message = self.message_post(
                body='Hi ' + ',' + 'Inspection Coordinator waiting for your Approval!',
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
            'event_status': 'submitforapproval',
        })

    @api.model_create_multi
    def create(self, vals_list):

        results = super(CalendarEvent, self).create(vals_list)
        for result in results:
            if result.unique_no:
                result.unique_no.write({'is_calendar_event_created':True })
            result.calendar_event_create_notification()
            result.action_submit()
            result.approve_statusbar1()
        return results

    def unlink(self):
        for record in self:
            if record.unique_no:
                other_events = self.env['calendar.event'].search([
                    ('unique_no', '=', record.unique_no.id),
                    ('id', '!=', record.id)
                ])

                if not other_events:
                    record.unique_no.write({
                        'is_calendar_event_created':False,
                        'calendar_count': 0
                        })

        return super(CalendarEvent, self).unlink()

    def write(self,vals):
        for record in self:
            if len(record.message_ids) > 0:
                if record.message_ids[0].body != '':
                    vals['last_message'] = record.message_ids[0].body
            if ((record.event_status == 'approved' and record.status in ['review', 'verified', 'submit']) and self.env.user.has_group('project_management.group_enquiry_coordinator')):
                raise UserError(_("You Cannot Modifiy the Calendar !!!"))

            if vals.get('approver_id') and ((record.status == 'open' and self.env.user.has_group('project_management.group_p4_coordinator')) and not self.env.user.has_group('base.group_system')):
                raise UserError(_("You Cannot Modifiy the Approver !!!"))
        return super(CalendarEvent,self).write(vals)
