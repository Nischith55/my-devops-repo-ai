# -*- coding: utf-8 -*-
"""Filter plugin to help with when to run tasks if multiple tasks are given"""
from __future__ import (absolute_import, division, print_function)
import os
import sys
sys.path.insert(0, 
    os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..",  "local-packages")))

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

from eiap.ansible.helpers import pprint_to_yaml
from eiap.ansible.mixins.display import DisplayMixin
from eiap.utils import (check_for_sequence,)

"""
# END Hack alert
"""

_D = DisplayMixin()

def run_if(tasks, allowed_list):
    '''runs if tasks contains any task which is in allowed_list'''
    check_for_sequence(tasks, 'tasks')
    check_for_sequence(tasks, 'allowed_list')
    _D.vvv("tasks:\n{}\nallowed_tasks:\n{}".format(pprint_to_yaml(tasks), pprint_to_yaml(allowed_list)))
    _allowed = set(allowed_list)
    _tasks = set(tasks)
    return len(_tasks.intersection(_allowed)) > 0

class FilterModule(object):
    ''' Ansible os helper'''
    
    def filters(self):
        return {
            'run_if' : run_if,
        }
    #
#
