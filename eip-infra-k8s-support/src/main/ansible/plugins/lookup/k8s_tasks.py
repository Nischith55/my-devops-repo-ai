# -*- coding: utf-8 -*-
"""
LookupModule: parse a task string and generate task params for generating
templates
"""
from __future__ import (absolute_import, division, print_function)
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

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
import traceback

from eiap.ansible.mixins.display import DisplayMixin
from eiap.ansible.lookup import LookupHelper
from eiap.ansible.tasks import TaskManager
from eiap.utils import (check_for_sequence,)

__metaclass__ = type

class LookupModule(LookupBase):

    def __init__(self, *args, **kwargs):
        super(LookupModule, self).__init__(*args, **kwargs)

    def run(self, task_str_list, variables=None, **kwargs): # @UnusedVariable (kwargs)
        check_for_sequence(task_str_list, 'task_str_list')
        _d = DisplayMixin()
        # NOTE: plugin loader should call the run method with variables=available_variables
        if variables is None:
            raise AnsibleError('No variables available in lookup environment')
        # create the lookup helper
        lookup_helper = LookupHelper(self._templar, variables, self._loader)
        try:
            task_mgr = TaskManager(lookup_helper)
            ret = []
            for task_str in task_str_list:
                tasks = task_mgr.parse_task(task_str)
                _d.f_console("** Tasks:\n{}", tasks)
                ret.extend(tasks)
            # for task
        except:
            traceback.print_exc()
        return ret

