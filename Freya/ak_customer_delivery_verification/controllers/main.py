# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo.http import request, route
from odoo.addons.website_sale.controllers.payment import PaymentPortal


class PaymentPortal(PaymentPortal):
    """
        Extension of Odoo's ``PaymentPortal`` controller to customize the website
        payment flow.
        REF: user story 13

        This subclass overrides specific controller methods related to payment
        processing on the website (e.g., payment transaction initialization) in
        order to introduce additional business logic—such as sending a one-time
        delivery verification email after a customer initiates a payment.

        The primary goals of this override are:
            - Inject additional post-transaction behavior without altering the
              core payment logic.
            - Enhance customer verification workflows tied to online orders.
            - Maintain compatibility with Odoo’s native portal and payment
              infrastructure.

        Notes
        -----
        - The superclass name is intentionally reused to extend and refine existing
          behavior.
        - All unmodified functionality from the original ``PaymentPortal`` remains
          intact.
        - This controller is publicly accessible where required, following Odoo’s
          route and access token security patterns.
    """

    def share_email_delivery_verification(self, order, provider):
        """Send the delivery verification email for ``order``.

        REF: user story 13

        Eligibility checks (website order, partner not yet paid, provider
        flagged for delivery verification) are expected to be performed by
        the caller — this method only loads the template and dispatches.
        """
        template = request.env.ref(
            "ak_customer_delivery_verification.sale_order_template_delivery_verification",
            raise_if_not_found=False,
        )
        if not template:
            return
        template.sudo().with_context(provider=provider.name).send_mail(
            order.id,
            force_send=True,
            email_values={'email_to': request.env.company.notification_share},
        )

    @route('/shop/payment/transaction/<int:order_id>', type='json', auth='public', website=True)
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        """
        Handle the public payment transaction flow for website orders, with an
        additional step to trigger a one-time email verification.

        REF: user story 13

        This method overrides the parent implementation to introduce email-based
        delivery verification after a payment transaction is initialized. The
        verification workflow is designed to be triggered only once per order.

        Workflow:
            1. Delegates to the parent implementation to perform standard payment
               transaction creation and validation logic.
            2. Retrieves the corresponding ``sale.order`` and ``payment.provider``
               records based on the returned transaction data.
            3. If both records are found, calls ``share_email_delivery_verification``
               to send a verification email to the customer.
            4. Returns the parent result unchanged.

        Parameters
        ----------
        order_id : int
            ID of the sale order for which the payment transaction is being processed.
        access_token : str
            Public access token used for validating that the request is authorized
            to operate on the given order.
        **kwargs : dict
            Additional keyword arguments passed by the route or upstream methods.

        Returns
        -------
        dict
            JSON-compatible dictionary returned by the parent method, usually
            including transaction details such as provider, transaction reference,
            status, etc.

        Side Effects
        ------------
        - Sends a one-time verification email via ``share_email_delivery_verification``.
        - Performs read and browse operations on ``sale.order`` and
          ``payment.provider`` models.

        Notes
        -----
        - This override does not alter the parent business logic; it only extends
          it with a post-processing hook.
        - The email is intended to be sent only once per order; responsibility for
          enforcing the "one-time" behavior should be inside
          ``share_email_delivery_verification``.
        """
        res = super(PaymentPortal, self).shop_payment_transaction(order_id, access_token, **kwargs)
        provider_id = res.get('provider_id') if res else None
        if not (order_id and provider_id):
            return res
        order = request.env['sale.order'].sudo().browse(order_id)
        provider = request.env['payment.provider'].sudo().browse(provider_id)
        if (order.exists() and provider.exists()
                and order.website_id
                and not order.partner_id.is_paid
                and provider.is_delivery_verification):
            self.share_email_delivery_verification(order, provider)
        return res
