/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { CalendarFormController } from "@calendar/views/calendar_form/calendar_form_controller";

/**
 * The Visit Summary form lets reviewers pick a radio option ("This event",
 * "This and following events", "All events") before clicking a workflow button
 * (Submit for Review, Submit for Approval, Approve, Reject, Re-Open, ...).
 *
 * Standard Odoo evaluates the button's `context=` AFTER `record.save()`, and
 * the save reloads the record — which re-fires the `recurrence_update`
 * compute and resets the radio to its default. So the user's selection is
 * lost before the server-side button method runs.
 *
 * Capture the current radio value BEFORE save, and inject it into the click
 * context as `button_recurrence_update`. Backend Python button methods (and
 * `write()`) read that context key to decide which subset of recurring events
 * to update.
 */
patch(CalendarFormController.prototype, {
    async beforeExecuteActionButton(clickParams) {
        const record = this.model.root;
        const recurrenceUpdate = record?.data?.recurrence_update;
        if (recurrenceUpdate) {
            // Replace the context entirely with a hard-coded literal of the
            // pre-save value. We cannot rely on the original
            // `{'button_recurrence_update': recurrence_update}` expression
            // because by the time it is evaluated (after the save reload) the
            // compute has already reset `recurrence_update` to its default.
            clickParams.context = `{'button_recurrence_update': '${recurrenceUpdate}'}`;
        }
        return super.beforeExecuteActionButton(clickParams);
    },
});
