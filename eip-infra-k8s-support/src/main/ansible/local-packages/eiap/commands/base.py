# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import sh

from ansible.errors import AnsibleError
from eiap.utils import (check_instance, check_for_string)
from eiap.ansible.lookup import LookupHelper
from eiap.ansible.mixins.display import DisplayMixin

class BaseCmd(DisplayMixin):
    """Convenient utility methods for the sh module

    Rules:
    - Base Classes MUST define 2 Class Variables:
        . v_cmd:  A variable that will be looked up via CLI to get the command
                  path.
        . d_cmd:  Default command path.
    - Never have a classmethod called 'create'
    """

    @classmethod
    def create(cls, lookup_helper, use_default_cmd):
        """Create the command instance"""
        try:
            cmd_path = lookup_helper.resolve_var(cls.v_cmd, default=cls.d_cmd) if use_default_cmd \
                        else lookup_helper.resolve_var(cls.v_cmd)
        except Exception as e:
            raise AnsibleError("[{}] variable pointing to binary path must be specified".format(cls.v_cmd), orig_exc=e)
        return cls(lookup_helper, cmd_path)

    def __init__(self, lookup_helper, cmd_path):
        super(BaseCmd, self).__init__()
        check_instance(lookup_helper, LookupHelper, "BaseCmd")
        self._lookup_helper = lookup_helper
        try:
            self._cmd = sh.Command(cmd_path)
        except Exception as e:
            raise AnsibleError("Failed to instantiate cmd: [{}]".format(cmd_path), orig_exc=e)

    def dynamic_call(self, method_name, *func_args, **func_kwargs):
        check_for_string(method_name, 'method_name')
        func = getattr(self, method_name)
        return func(*func_args, **func_kwargs)

    def __repr__(self):
        return "Command: [{}]".format(self._cmd)

    __str__ = __repr__
