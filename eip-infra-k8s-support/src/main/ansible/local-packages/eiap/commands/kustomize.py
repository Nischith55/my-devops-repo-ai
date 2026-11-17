# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import sh
import six
import yaml

from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native

from copy import deepcopy

from eiap.deepmerge_mergers import merge_list_override
from eiap.utils import (check_for_mapping,)

from .base import BaseCmd

class KustomizeCmd(BaseCmd):
    """Class that encapsulates kustomize command via sh module.
    """
    v_cmd = 'kustomize_cmd'
    d_cmd = 'kustomize'

    d_build_cmd_args_v4 = {
        #'enable-managedby-label': True,
        'reorder': 'legacy',
        'load-restrictor': 'LoadRestrictionsNone',
    }

    d_build_cmd_args_v3 = {
        #'enable-managedby-label': True,
        'reorder': 'legacy',
        'load_restrictor': 'LoadRestrictionsNone',
    }

    def __init__(self, lookup_helper, cmd_path):
        super(KustomizeCmd, self).__init__(lookup_helper, cmd_path)
        version_out_obj = self._cmd("version")
        self._build_flags = dict()
        # HACK Alert: encoding retrieved from call_args undocumented
        encoding = version_out_obj.call_args["encoding"]
        version_out = version_out_obj.stdout.decode(encoding) if six.PY3 else version_out_obj.stdout
        if version_out.startswith('{Version:kustomize/v4'):
            self._build_flags.update(self.d_build_cmd_args_v4)
        elif version_out.startswith('{Version:kustomize/v3'):
            self._build_flags.update(self.d_build_cmd_args_v3)
        else:
            raise AnsibleError("Only kustomize version 3.x and 4.x series supported. [{}]".format(version_out))

    def build(self, src_dir, flags=None):
        build_flags = deepcopy(self._build_flags)
        if flags is not None:
            check_for_mapping(flags, "flags")
            merge_list_override.merge(build_flags, flags)
        cmd_args = list()
        '''kustomize 3.x has underscores in arguments, which gets converted to - in sh, sigh'''
        for k, v in six.iteritems(build_flags):
            cmd_args.append('--' + k)
            if isinstance(v, six.string_types):
                cmd_args.append(v)
            elif isinstance(v, bool):
                # remove last element keyword if false
                if not v:
                    cmd_args.pop()
            else:
                self.warning("Illegal value type, ignore keyword [{}]".format(v))
                cmd_args.pop()
        try:
            ''' Note Command returns an instance of sh.RunningCommand'''
            cmd_run_obj = self._cmd('build', src_dir, *cmd_args)
        except sh.ErrorReturnCode as e:
            raise AnsibleError("Failed to build src_dir: [{}], error: [{}]".format(src_dir, to_native(e.message)), orig_exc=e)
        self.f_vvv("cmd_run_obj:\n{}", cmd_run_obj)
        k8s_rescs = list(filter(None, yaml.safe_load_all(cmd_run_obj.stdout)))
        return k8s_rescs
