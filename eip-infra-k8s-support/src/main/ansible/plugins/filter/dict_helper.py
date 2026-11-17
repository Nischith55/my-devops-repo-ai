# -*- coding: utf-8 -*-
"""Filter plugin with additional filters for working with objects"""

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError, AnsibleFilterError
from ansible.module_utils.common._collections_compat import Mapping
from ansible.utils.display import Display
from json import dumps


display = Display()

def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
        #
    #
    return dct

def find_keys(mapping, key):
    '''Find all keys in the given mapping recursively'''
    if isinstance(mapping, list):
        for i in mapping:
            for x in find_keys(i, key):
               yield x
    elif isinstance(mapping, dict):
        if key in mapping:
            yield mapping[key]
        for j in mapping.values():
            for x in find_keys(j, key):
                yield x

def del_key(map, key):
    '''delete a key from map -- ONLY top level key'''
    display.vvv("[delete_key]: key: {0}, map:[{1}]".format(key, dumps(map, indent=2)))
    if isinstance(map, Mapping):
        if key in map:
            del map[key]
    return map

class FilterModule(object):
    ''' Ansible dict helper filters '''
    
    def filters(self):
        return {
            'del_key': del_key,
            'dict_merge' : dict_merge,
            'find_keys' : find_keys,
            'makedict': lambda _val, _list: { k: _val for k in _list },
        }
    #
#
