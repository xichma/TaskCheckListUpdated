# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.depends('task_checklist')
    def _checklist_progress(self):
        """:return the value for the check list progress"""
        for rec in self:
            total_len = self.env['task.checklist'].search_count([])
            check_list_len = len(rec.task_checklist)
            if total_len != 0:
                rec.checklist_progress = (check_list_len * 100) / total_len

    task_checklist = fields.Many2many('task.checklist', string='Check List')
    checklist_progress = fields.Float(compute=_checklist_progress, string='Progress', store=True,
                                      default=0.0)
    max_rate = fields.Integer(string='Maximum rate', default=100)


class TaskChecklist(models.Model):
    _name = 'task.checklist'
    _description = 'Checklist for the task'

    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description')


class CheckList(models.Model):
    _name = 'check.list'
    name = fields.Char('Name')
    description = fields.Text('Description')
    status = fields.Selection(string="Status",
                              selection=[('done', 'Done'), ('progress', 'In Progress'), ('cancel', 'Cancel')],
                              readonly=True, track_visibility='onchange')

    def do_accept(self):
        self.write({
            'status': 'done',
        })
        # return {'type': 'ir.actions.client', 'tag': 'reload'}

    def do_cancel(self):
        self.write({
            'status': 'cancel',
        })
        # return {'type': 'ir.actions.client', 'tag': 'reload'}

    def do_progress(self):
        self.write({
            'status': 'progress',
        })
        # return {'type': 'ir.actions.client', 'tag': 'reload'}

    def do_set_to(self):
        self.write({
            'status': ''
        })

    class CustomProject(models.Model):
        _inherit = 'project.task'
        info_checklist = fields.One2many(comodel_name="check.list", inverse_name="name", required=True,
                                         track_visibility='onchange')
        progress_rate = fields.Integer(string='Checklist Progress', compute="check_rate")
        total = fields.Integer(string="Max")
        status = fields.Selection(string="Status",
                                  selection=[('done', 'Done'), ('progress', 'In Progress'), ('cancel', 'Cancel')],
                                  readonly=True, track_visibility='onchange')

        maximum_rate = fields.Integer(default=100)

        def check_rate(self):
            for rec in self:
                rec.progress_rate = 0
                total = len(rec.info_checklist.ids)
                done = 0
                cancel = 0
                if total == 0:
                    pass
                else:
                    if rec.info_checklist:
                        for item in rec.info_checklist:
                            if item.status == 'done':
                                done = done + 1
                            rec.progress_rate = round(done / (total - cancel), 2) * 100
