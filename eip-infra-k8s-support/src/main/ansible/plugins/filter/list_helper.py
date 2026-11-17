# -*- coding: utf-8 -*-
"""Filter plugin to search a list of objects with one unique key"""

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from copy import deepcopy

from ansible.errors import AnsibleError, AnsibleFilterError
from ansible.module_utils.common._collections_compat import MutableSequence, Mapping
from ansible.utils.display import Display



display = Display()

def search_list(objects, key, value, key1=None, value1=None):
    '''Build complete URI body param for vnet'''
    display.vv("key: [%s]" % key)
    display.vv("value: [%s]" % value)
    display.vv("key1: [%s]" % key1)
    display.vv("value1: [%s]" % value1)
    
    if not isinstance(objects, MutableSequence):
        raise AnsibleFilterError("'objects' requires a sequence, got %s instead." % type(objects))
    
    ret = []
    for obj in objects:
        # Expect any type of Mapping
        if not isinstance(obj, Mapping):
            raise AnsibleError("'obj' expects a dict")
        if key not in obj:
            raise AnsibleError("key [%s] not found" % key)
        else:
            if key1 is not None and value1 is not None:
                if obj[key] == value and obj[key1] == value1:
                    ret.append(obj)
            elif obj[key] == value and (key1 is None and value1 is None):
                ret.append(obj)
            #
        #
    if len(ret) > 1 or len(ret) == 0:
        raise AnsibleFilterError("Multiple or no obj found with key:[{0}], value:[{1}] and key1:[{2}], value1:[{3}]".format(key, value, key1, value1))
    return ret[0]

class FilterModule(object):
    ''' Ansible search list'''
    
    def filters(self):
        return {
            'search_list' : search_list,
        }
    #
#
