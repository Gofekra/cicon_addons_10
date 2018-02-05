from odoo import models, api
from calendar import Calendar
import  sys


class PmSchPlanReport(models.AbstractModel): # Report File Name
    _name = 'report.cmms.cmms_pm_plan_report_template'

    @api.model
    def render_html(self,docids, data=None):
        data = data if data is not None else {}
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('cmms.cmms_pm_plan_report_template')
        _docs = self._get_date_list(data.get('ids', data.get('active_ids')))
        docargs = {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'doc_model': report.model,
            'docs': _docs,
            'heading': self._context.get('heading'),
            'sub_heading': self._context.get('sub_heading', False),
            'get_pm_detail': self._get_pm_details
        }
        #print docargs
        return report_obj.render('cmms.cmms_pm_plan_report_template', docargs)

    def _get_date_list(self,data):
        _cal = Calendar(5)
        _date = list(_cal.itermonthdates(self._context.get('rpt_year'), self._context.get('rpt_month')))
        return _date

    def _get_duration(self, _duration):
        _duartion_to_hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(_duration * 60, 60))
        _task_duration = str(_duartion_to_hour)
        return _task_duration

    def _get_pm_details(self, _pm_date):
        _pm_list = {}
        if _pm_date:
            _sch_obj = self.env['cmms.pm.schedule.master']
            _sch_recs = _sch_obj.search([('next_date', '=', _pm_date), ('company_id', '=', self.env.user.company_id.id)])
            if _sch_recs:
                _interval = _sch_recs.mapped('interval_id')
                for _intv in _interval:
                    _sch_intv = _sch_recs.filtered(lambda r: r.interval_id.id == _intv.id)
                    _machines = _sch_intv.mapped('machine_ids')
                    if self._context.get('machine_type_ids',False):
                        _machines = _machines.filtered(lambda m: m.type_id.id in self._context.get('machine_type_ids'))
                    _m_task_count = {}
                    for m in _machines:
                        _sch_intv_machine = _sch_intv.filtered(lambda r: m in r.machine_ids)
                        _pm_task_ids = _sch_intv_machine.mapped('pm_task_ids')
                        _duration = sum([x.duration for x in _pm_task_ids])
                        _pm_task_duration = self._get_duration(_duration)
                        _m_task_count[m.code] = str(len(_sch_intv_machine.mapped('pm_task_ids'))) + '[' + _pm_task_duration + ']'
                        #print _pm_task_duration
                    if _m_task_count:
                        _pm_list[_intv.name] = _m_task_count
        return _pm_list


