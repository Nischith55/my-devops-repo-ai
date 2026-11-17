# -*- coding: utf-8 -*-
"""Filter plugin miscellaneous utils"""

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

def remove_prefix(text, prefix):
    _check_for_string(text, 'text')
    _check_for_string(prefix, 'prefix')
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def shorten(name):
    """shorten a azure resource name"""
    _check_for_string(name, 'resource name')
    _name_short_map = {
        'pep-eiap-nonprod-scus-' : 'pe1001',
        'pep-eiap-nonprod-ncus-' : 'pe1002',
        'pep-eiap-nonprod-eus-' : 'pe1003',
        'pep-eiap-nonprod-suk-' : 'pe1004',
        'pep-eiap-nonprod-gwc-' : 'pe1005',
        'pep-eiap-nonprod-sea-' : 'pe1006',
        'pep-eiap-nonprod-ae-' : 'pe1007',
        # preprod
        'pep-eiap-preprod-scus-' : 'pe2001',
        'pep-eiap-preprod-ncus-' : 'pe2002',
        'pep-eiap-preprod-eus-' : 'pe2003',
        'pep-eiap-preprod-suk-' : 'pe2004',
        'pep-eiap-preprod-gwc-' : 'pe2005',
        'pep-eiap-preprod-sea-' : 'pe2006',
        'pep-eiap-preprod-ae-' : 'pe2007',
        # prod
        'pep-eiap-prod-scus-' : 'pe3001',
        'pep-eiap-prod-ncus-' : 'pe3002',
        'pep-eiap-prod-eus-' : 'pe3003',
        'pep-eiap-prod-suk-' : 'pe3004',
        'pep-eiap-prod-gwc-' : 'pe3005',
        'pep-eiap-prod-sea-' : 'pe3006',
        'pep-eiap-prod-ae-' : 'pe3007',
    }
    ret = name
    for k, v in _name_short_map.iteritems():
        if name.startswith(k):
            _n = v
            ret = v + '-' + remove_prefix(name, k)
            break
    return ret
#

def join_trim(items, join_str, strip=True, ignore_empty=True):
    """Join a list of strings with given join character
    
    By default each item is stripped, unless strip is 'False' and empty strings
    are ignored note strip has no effect on empty strings.
    """
    _check_for_sequence(items, 'items')
    _check_for_string(join_str, 'join_str')
    _items = []
    for i in items:
        if i is None:
            continue
        _check_for_string(i, 'item')
        if ignore_empty and (i.strip() == ''):
            continue
        _items.append(i.strip() if strip else i)
    #
    ret = join_str.join(_items).strip()
    display.v("ret: [{0}]".format(ret))
    return ret

class FilterModule(object):
    ''' Ansible misc_utils'''
    
    def filters(self):
        return {
            'join_trim': join_trim,
            'remove_prefix': remove_prefix,
            'shorten': shorten,
        }
    #
#
