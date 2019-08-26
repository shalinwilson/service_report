import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons import decimal_precision as dp


class ReportServiceReport(models.AbstractModel):
    _name = "report.kims_service_report.report_service_details"

    @api.model
    def get_service_details(self, start_date=False, end_date=False):
        """ Serialise the orders of the day information

        params: start_date, end_date string representing the datetime of order
        """
        print('enter')
        user_tz = pytz.timezone(self.env.context.get(
            'tz') or self.env.user.tz or 'UTC')
        today = user_tz.localize(fields.Datetime.from_string(
            fields.Date.context_today(self)))
        today = today.astimezone(pytz.timezone('UTC'))
        if start_date:
            start_date = fields.Datetime.from_string(start_date)
        else:
            # start by default today 00:00:00
            start_date = today

        if end_date:
            # set time to 23:59:59
            end_date = fields.Datetime.from_string(end_date)
        else:
            # stop by default today 23:59:59
            end_date = today + timedelta(days=1, seconds=-1)

        # avoid a end_date smaller than start_date
        end_date = max(end_date, start_date)

        start_date = fields.Datetime.to_string(start_date)
        end_date = fields.Datetime.to_string(end_date)


        query = """

with cte as (
select sum(sol.price_total) as order_total,so.id as so_id ,so.sale_reference, so.date_order
from  sale_order_line as sol
left join sale_order as so on   sol.order_id = so.id
left join product_product as pp on sol.product_id = pp.id
  left join product_template as pt on   pp.product_tmpl_id = pt.id

  where pt.name != 'Service Charge' and sol.order_id in ( select so.id
  FROM  sale_order_line as sol
 left join sale_order as so on   sol.order_id = so.id
 left join product_product as pp on sol.product_id = pp.id
  left join product_template as pt on   pp.product_tmpl_id = pt.id
WHERE  pt.name = 'Service Charge')

group by so.id


)
select cte.so_id ,cte.sale_reference,order_total,sol.price_total as service_charge,round((sol.price_total/order_total)*100,2) as service_charge_percent
FROM  sale_order_line as sol
 left join cte on   sol.order_id = cte.so_id
 left join product_product as pp on sol.product_id = pp.id
  left join product_template as pt on   pp.product_tmpl_id = pt.id
 WHERE  pt.name = 'Service Charge'
  and cte.date_order between %s and %s
  ;
"""
        self.env.cr.execute(query,[start_date,end_date])
        psqldata = self._cr.fetchall()
        datalist = []
        for record in psqldata:
            datalist.append({'soid':record[1],'pricettl':record[2],'taxamount':record[3],'taxpercent':record[4],})
        return {
            'datarow': datalist,
            'start_date':start_date,
            'end_date':end_date
        }

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_service_details(data['start_date'], data['end_date']))
        return data
