# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from ansible.errors import AnsibleError, AnsibleAssertionError
from ansible.module_utils._text import to_native
from copy import deepcopy

import sh
import os
import yaml

from eiap.utils import (check_for_mapping, check_for_string)
from eiap.deepmerge_mergers import merge_list_override

from .base import BaseCmd

class IstioctlCmd(BaseCmd):
    """Class that encapsulates Istioctl command via sh module.
    """
    v_cmd = 'istioctl_cmd'
    d_cmd = 'istioctl'
    
    d_operator_dump_flags = {
        "operatorNamespace": "istio-operator",
    }

    yaml_dump_options = {
        'explicit_start': True,
        'default_flow_style': False,
        'indent': 2,
    }


    def __init__(self, lookup_helper, cmd_path):
        super(IstioctlCmd, self).__init__(lookup_helper, cmd_path)

    def operator_dump(self, flags, output=None, **kwargs):
        check_for_mapping(flags, "flags")
        cmd_flags = merge_list_override.merge(deepcopy(self.d_operator_dump_flags), flags)
        required_flags = ('revision',)
        for _f in required_flags:
            if _f not in cmd_flags:
                raise AnsibleAssertionError("Flag [{}] is required".format(_f))

        try:
            ''' Note Command returns an instance of sh.RunningCommand'''
            output_cmd = self._cmd('operator', 'dump', **cmd_flags)
        except sh.ErrorReturnCode as e:
            raise AnsibleError("Failed to execute command: [{}], error: [{}]".format(self._cmd, to_native(e.message)), orig_exc=e)
        self.f_vvvv("output_cmd:\n{}", output_cmd)
        '''NOTE: filter out blank documents, yest that's possible and safe load'''
        k8s_rescs = list(filter(None, yaml.safe_load_all(output_cmd.stdout)))
        output_path = None
        if output is not None:
            output_path = os.path.realpath(os.path.expandvars(os.path.expanduser(output)))
        elif 'output_path_var' in kwargs:
            output_path_val = self._lookup_helper.resolve_var(kwargs['output_path_var'], default=None)
            if output_path_val is not None:
                output_path = os.path.realpath(os.path.expandvars(os.path.expanduser(output_path_val)))
        if output_path is not None:
            check_for_string(output_path, "output_path")
            with open(output_path, "w") as ofd:
                yaml.safe_dump_all(k8s_rescs, ofd, **self.yaml_dump_options)
        self.f_vvv("k8s_rescs:\n{}", k8s_rescs)
        return k8s_rescs
