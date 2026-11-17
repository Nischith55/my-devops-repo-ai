# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
from ansible.errors import AnsibleAssertionError, AnsibleActionFail
__metaclass__ = type

import os
import sys


"""
# #############################################################################
# IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT 
# Hack Alert:
# - Ansible does NOT allow *any* plugins to important python libraries except
#   except for what is in ansible.* namespace.
# - To overcome this we will use sys.path.insert to import OUR or any 3rd party
#   libraries
# - IMPORTANT: we use relative path as per this file location
# #############################################################################
# BEGIN HACK -- Check the relative path, if the file is moved PLEASE change
#               accordingly the python-libs location
"""
sys.path.insert(0, 
    os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..",  "local-packages")))
"""
# END Hack alert
"""

from ansible.plugins.action import ActionBase

from copy import deepcopy

from eiap.ansible.mixins.display import DisplayMixin
from eiap.ansible.lookup import LookupHelper
from eiap.ansible.tasks import TaskManager

class ActionModule(ActionBase, DisplayMixin):

    TRANSFERS_FILES = False # determine if tmp path needs to be created before action is executed.

    # Free-form
    _VALID_ARGS = frozenset([])

    MANDATORY_ARGS = (
        'task_str',
    )
    DEFAULT_NEWLINE_SEQUENCE = "\n"

    def _ensure_invocation(self, result):
        # NOTE: adding invocation arguments here needs to be kept in sync with
        # any no_log specified in the argument_spec in the module.
        if 'invocation' not in result:
            if self._play_context.no_log:
                result['invocation'] = "CENSORED: no_log is set"
            else:
                result['invocation'] = self._task.args.copy()
                result['invocation']['module_args'] = self._task.args.copy()

        return result

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        variables = deepcopy(self._templar._available_variables)
        variables['_check_mode_'] = self._play_context.check_mode
        variables['_diff_mode_'] = self._play_context.diff
        lookup_helper = LookupHelper(self._templar, variables, self._loader)
        for _a in self.MANDATORY_ARGS:
            if _a not in self._task.args:
                raise AnsibleActionFail("required arg: [{}]".format(_a))
        task_str = self._task.args['task_str']
        task_args = deepcopy(self._task.args)
        task_args.pop('task_str', None)
        task_mgr = TaskManager(lookup_helper)
        self.f_vv("TaskManager:\n{}", task_mgr)
        task_result = task_mgr.handle_task(task_str, **task_args)
        result['changed'] = task_result.changed
        result['skipped'] = task_result.skipped
        if self._play_context.diff:
            result['diff'] = task_result.data
        else:
            result['msg'] = task_result.data
        return self._ensure_invocation(result)

