# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
from lxml import etree

import datetime
from dateutil import tz
import pytz
import time
from string import Template
from datetime import datetime, timedelta
from odoo.exceptions import  Warning
from pdb import set_trace as bp

from itertools import groupby
from operator import itemgetter

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)  # Need for message in console.



class ProjectTaskNativeResource(models.Model):
    _name = 'project.task'
    _inherit = 'project.task'

    task_resource_ids = fields.One2many('project.task.resource.link', 'task_id', 'Resources')


class ProjectTaskResourceLink(models.Model):
    _name = 'project.task.resource.link'
    _description = "project.task.resource.link"

    _order = 'date_start'

    @api.model
    def _get_load_control(self):
        value = [
            ('no', _('No')),
            ('in_project', _('In project')),
            ('everywhere', _('Everywhere')),
        ]
        return value

    name = fields.Char(compute='_compute_name_link', readonly=True, store=False)

    resource_id = fields.Many2one('resource.resource', 'Resource', ondelete='restrict')
    task_id = fields.Many2one('project.task', 'Task', ondelete='cascade', readonly=True,)
    load_factor = fields.Float("Load Factor", default=1.0)

    resource_type = fields.Selection(string='Type', related="resource_id.resource_type", readonly=True, store=True)
    date_start = fields.Datetime(related='task_id.date_start', string="Date Start",  store=True, readonly=True,)
    date_end = fields.Datetime(related='task_id.date_end', string="Date End",  store=True, readonly=True,)
    duration = fields.Integer(related='task_id.native_duration', string='Duration',  store=True, readonly=True,)
    project_id = fields.Many2one(related='task_id.project_id', string='Project', store=True, readonly=True,)
    active_task = fields.Boolean(related='task_id.active', string="Archived", store=True, readonly=True, )

    # load_control = fields.Boolean(name="Load Control", help="Allow Resource Load Control", default=True)
    load_control = fields.Selection('_get_load_control',
                                    string='Load Control',
                                    required=True,
                                    default='everywhere')

    color_gantt_set = fields.Boolean("Set Color Task", default=True)
    color_gantt = fields.Char(
        string="Color",
        store=True,
        default='rgba(190,170,23,0.53)'
    )




    @api.depends('task_id', 'load_factor', 'resource_id', 'resource_type')
    def _compute_name_link(self):
        for task in self:
            task.name = "{}-{} ({}) {}".format(task.project_id.name or "", task.task_id.name or "", task.resource_id.name, task.load_factor or "")



    def write(self, vals):

        result = super(ProjectTaskResourceLink, self).write(vals)
        if result:
            info_name = "res_{}".format(self.id)
            info_task = self.env['project.task.info'].sudo().search([('name', '=', info_name)])
            if info_task.id:
                info_task.sudo().write({"end": self.resource_id.name})

        return result



    def unlink(self):
        res = super(ProjectTaskResourceLink, self).unlink()

        if res:
            for res_id in self:
                self.env['project.task'].sudo()._task_info_remove(info_name="res_{}".format(res_id.id))

        return res

    @api.model_create_multi
    def create(self, vals):

        new_id = super(ProjectTaskResourceLink, self).create(vals)

        if new_id:
            info_name = "res_{}".format(new_id.id)
            value = {}
            value["name"] = info_name
            value["end"] = new_id.resource_id.name
            value["show"] = True

            vals = {}
            vals["info_ids"] = [(0, 0, value)]
            new_id.task_id.write(vals)

        return new_id



    _sql_constraints = [
            ('project_task_resource_link_uniq', 'unique(task_id, resource_id)', 'Duplicate Resource.'),
        ]



