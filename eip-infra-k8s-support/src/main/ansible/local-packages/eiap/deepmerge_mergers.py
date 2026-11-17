# -*- coding: utf-8 -*-
'''
Module to wrap deepmerge mergers with EIAP merge requirements for REST
API calls
'''

from __future__ import (absolute_import, division, print_function)

from deepmerge.merger import Merger

'''
merge_list_override:
 - for list values, the nxt will OVERRIDE the base one
 - this merge will never raise an exception.
 - in the case of type mismatches (applies to all types),
     - the value from the second object will override the previous one.

'''
merge_list_override = Merger(
    [
        (list, "override"),
        (dict, "merge")
    ],
    ["override"],
    ["override"]
)

'''
merge_list_append:
 - for list values, the nxt will APPEND to the base one
 - this merge will never raise an exception.
 - in the case of type mismatches (applies to all types),
     - the value from the second object will override the previous one.

'''
merge_list_append = Merger(
    [
        (list, "append"),
        (dict, "merge")
    ],
    ["override"],
    ["override"]
)

'''
merge_list_prepend:
 - for list values, the nxt will PREPEND to the base one
 - this merge will never raise an exception.
 - in the case of type mismatches (applies to all types),
     - the value from the second object will override the previous one.

'''
merge_list_prepend = Merger(
    [
        (list, "prepend"),
        (dict, "merge")
    ],
    ["override"],
    ["override"]
)
