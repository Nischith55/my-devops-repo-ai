"""Filter plugin to help with manifest operations like kustomize"""

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common._collections_compat import Mapping, Sequence, MutableSequence
from ansible.module_utils.six import string_types
from ansible.utils.display import Display

from copy import deepcopy
from json import dumps

import os

__metaclass__ = type

display = Display()

def _check_for_sequence(obj, name):
    '''Utility method to check for sequence'''
    if not isinstance(obj, MutableSequence):
        raise AnsibleFilterError("{0} must be a Sequence type. Got {1}".format(name, type(obj)))
    #

def _check_for_mapping(obj, name):
    '''Utility method to check for mapping'''
    if not isinstance(obj, Mapping):
        raise AnsibleFilterError("{0} must be a Mapping type. Got {1}. {2}".format(name, type(obj), obj))
    #

def _check_for_string(obj, name):
    '''Utility method to check for string'''
    if not isinstance(obj, string_types):
        raise AnsibleFilterError("{0} must be a string type. Got {1}".format(name, type(obj)))
    #

def get_component_setting(apps_setting_all, app_name, component_name):
    """Searh a list of all apps or add-ons settings and extract the component settings for an app"""
    _check_for_sequence(apps_setting_all, 'apps_setting_all')
    _check_for_string(app_name, 'app_name')
    _check_for_string(component_name, 'component_name')
    display.vvvv("apps_setting_all: {0}".format(dumps(apps_setting_all, indent=2)))

    for _as in apps_setting_all:
        _aname = _as['name']
        if _aname == app_name:
            for _cs in _as.get('components', []):
                _csname = _cs['name']
                if _csname == component_name:
                    ret = deepcopy(_cs)
                    return ret
        
    #
    # error if we cannot find..
    raise AnsibleFilterError("Could not find component settings for app: [{0}], component: [{1}]".format(app_name, component_name))

class FilterModule(object):
    ''' Ansible os helper'''
    
    def filters(self):
        return {
            'get_component_setting': get_component_setting,
        }
    #
#
