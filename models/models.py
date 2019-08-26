# from odoo import models, fields, api
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError

class SaleServiceWizard(models.TransientModel):

    _name = 'service.wizard.report'

    start_date=fields.Datetime('Start Date')
    end_date=fields.Datetime('End Date')
   

   
    @api.multi
    def sale_report(self):
        data = {'start_date': self.start_date, 'end_date': self.end_date}
        return self.env.ref('kims_service_report.sale_servicetax_details_report').report_action([], data=data)

