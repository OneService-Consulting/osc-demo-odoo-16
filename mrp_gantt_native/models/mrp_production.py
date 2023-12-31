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

_logger = logging.getLogger(__name__) # Need for message in console.


class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ['mrp.production']

    #Sorting
    sorting_seq = fields.Integer(string='Sorting Seq.')
    sorting_level = fields.Integer('Sorting Level', default=0)
    sorting_level_seq = fields.Integer('Sorting Level Seq.', default=0)


    #Gantt
    is_milestone = fields.Boolean("Mark as Milestone", default=False)
    on_gantt = fields.Boolean("Task name on gantt", default=False)


    # link
    predecessor_ids = fields.One2many('mrp.production.predecessor', 'task_id', 'Links')
    predecessor_count = fields.Integer(compute='_compute_predecessor_count', string='Predecessor Count', store=True)
    predecessor_parent = fields.Integer(compute='_compute_predecessor_count', string='Predecessor parent', store=True)


    @api.depends("predecessor_ids")
    def _compute_predecessor_count(self):

        for task in self:
            for predecessor in task.predecessor_ids:
                predecessor.parent_task_id.write({
                    'predecessor_parent': 1,
                })

            search_if_parent = self.env['mrp.production.predecessor'].sudo().search_count(
                [('parent_task_id', '=', task.id)])

            task.update({
                'predecessor_count': len(task.predecessor_ids),
                'predecessor_parent': search_if_parent,
            })



    #MRP
    date_planned_deadline = fields.Datetime(
        'Deadline Gantt', copy=False, default=fields.Datetime.now,
        index=True,
        readonly=True,
        states={'confirmed': [('readonly', False)]})


    # date_planned_start = fields.Datetime(
    #     'Deadline Start', copy=False, default=fields.Datetime.now,
    #     index=True, required=True,readonly=True,
    #     states={'confirmed': [('readonly', False)]}, oldname="date_planned")

    # date_planned_finished = fields.Datetime(
    #     'Deadline End', copy=False, default=fields.Datetime.now,
    #     index=True,readonly=True,
    #     states={'confirmed': [('readonly', False)]})



    @api.model
    def childs_get(self, ids_field_name, ids, fields):

        test = "OK"
        return test



