/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { AttendeeCalendarModel } from "@calendar/views/attendee_calendar/attendee_calendar_model";

/**
 * FullCalendar uses dayMaxEventRows from model.eventLimit (see calendar arch
 * event_limit, default 5). Returning false disables the per-day cap so every
 * event row is visible without "+N more".
 */
patch(AttendeeCalendarModel.prototype, {
    get eventLimit() {
        return false;
    },
});