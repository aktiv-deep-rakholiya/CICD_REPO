# -*- coding: utf-8 -*-

from odoo import api, models


class ReportTimesheetPdfTurkstream(models.AbstractModel):
    _name = 'report.zip_reports.report_timesheet_pdf_turkstream'
    _description = 'Timesheet PDF Turkstream'

    @api.model
    def _get_report_values(self, docids, data=None):

        docs = self.env['calendar.event'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': 'calendar.event',
            'docs': docs,
            'data': data or {},
        }
