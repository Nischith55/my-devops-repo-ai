# -*- coding: utf-8 -*-
"""Filter plugin to help with built-in python os module"""

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.collections import is_sequence
from ansible.module_utils.six import string_types
from ansible.utils.display import Display



display = Display()

#: NOTE: this is built-in in ansible 2.10 > stop gap for now
def path_join(paths):
    ''' takes a sequence or a string, and return a concatenation
        of the different members '''
    if isinstance(paths, string_types):
        return os.path.join(paths)
    elif is_sequence(paths):
        return os.path.join(*paths)
    else:
        # NOTE 2.10 has AnsibleFilterTypeError
        raise AnsibleFilterError("|path_join expects string or sequence, got %s instead." % type(paths))

class FilterModule(object):
    ''' Ansible os helper'''
    
    def filters(self):
        return {
            'path_join' : path_join,
        }
    #
#
