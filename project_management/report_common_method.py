

def send_report_notification(env, file_name, file_data, res_model, res_id, group_xmlid='project_management.accounts_role', body=None):
    """
    Sends a notification with attachment to all users in a given security group.

    :param env: Odoo Environment (self.env)
    :param file_name: Name of the file (e.g. report.zip)
    :param file_data: Base64-encoded file data
    :param res_model: Model name of the record generating this file
    :param res_id: ID of the record generating this file
    :param group_xmlid: XML ID of the security group
    :param body: Optional message body
    """

    # Default body message
    body = body or "Report has been generated. Kindly review it!"

    # Get users in the group
    group = env.ref(group_xmlid, raise_if_not_found=False)
    if not group:
        return False

    users = env['res.users'].search([('groups_id', 'in', [group.id])])
    partners = users.mapped('partner_id')

    if not partners:
        return False

    # Create attachment
    attachment = env['ir.attachment'].sudo().create({
        'name': file_name,
        'type': 'binary',
        'datas': file_data,
        'res_model': res_model,
        'res_id': res_id,
        'mimetype': 'application/zip'
    })

    # Post message + notification to each partner
    for partner in partners:
        message = partner.message_post(
            body=body,
            message_type='notification',
            attachment_ids=[attachment.id],
            subtype_xmlid="mail.mt_comment",
        )
        env['mail.notification'].create({
            'mail_message_id': message.id,
            'res_partner_id': partner.id,
            'notification_type': 'inbox',
            'is_read': False,
        })

def update_summary_and_emp_lists(env, calendar_event, fromdate, todate, month_data):
    """
    Common reusable function to create/update summary.report and emp.list records
    based on given calendar.event records.

    :param env: Odoo Environment (self.env)
    :param calendar_event: recordset of calendar.event
    :param fromdate: starting date (datetime.date)
    :param todate: ending date (datetime.date)
    :param month_data: custom month data string (optional)
    :return: list of project_ids processed
    """
    summary_obj = env['summary.report']
    emp_obj = env['emp.list']

    # Preload all summary records for efficiency
    all_summaries = summary_obj.search([])
    existing_calendar_ids = set(all_summaries.mapped('emp_list').mapped('calendar_ids').ids)

    project_ids = []

    for rec in calendar_event:
        if not rec:
            continue

        already_linked = rec.id in existing_calendar_ids

        summary_exists = summary_obj.search([
            ('date_from', '>=', fromdate),
            ('date_to', '<=', todate),
            ('project_id', '=', rec.project_id.id),
            ('approve', '=', False),
            ('not_approve', '=', False)
        ], limit=1)

        emp_vals = {
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
            "overnight_expense": rec.overnight_expense,
            "without_stay": rec.without_stay,
            "calendar_ids": rec.ids,
            "partner_ids": rec.vendor_id.ids,
            "purchase_id": rec.purchase_id.id,
            "tax_id": rec.client_id.tax_ids.ids,
        }

        emp_exists = emp_obj.search([('calendar_ids', 'in', rec.ids)], limit=1, order='id desc')

        if summary_exists and (not summary_exists.approve and not summary_exists.not_approve):
            # Existing summary, update or add emp.list
            if emp_exists:
                if already_linked or rec not in emp_exists.calendar_ids:
                    emp_exists.write(emp_vals)
            else:
                summary_exists.write({'emp_list': [(0, 0, emp_vals)]})
        else:
            # No summary, create new one
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
                "month_data": month_data,
                "date": fromdate,
                "date_from": fromdate,
                "date_to": todate,
                "emp_list": [(0, 0, emp_vals)],
            }
            summary_obj.create(vals)

        project_ids.append(rec.project_id.id)
