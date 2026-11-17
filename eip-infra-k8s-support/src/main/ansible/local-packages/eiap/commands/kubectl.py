# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import os
import re
import sh
import six
import yaml

from ansible.errors import (AnsibleError, AnsibleAssertionError, )
from ansible.module_utils._text import to_native

from datetime import timedelta

from eiap.utils import (check_for_mapping, check_for_sequence,)
from eiap.constants import K8SConstants

from timeit import default_timer as timer

from .base import BaseCmd
from eiap.ansible.helpers import pprint_to_yaml

class KubectlCmd(BaseCmd):
    """Class that encapsulates kubectl command via sh module.
    """
    v_cmd = 'kubectl_cmd'
    d_cmd = 'kubectl'

    diff_search_expr = re.compile(r'^diff .*?(?=[\r\n]+diff |\Z)', re.MULTILINE|re.DOTALL)

    def __init__(self, lookup_helper, cmd_path):
        super(KubectlCmd, self).__init__(lookup_helper, cmd_path)
        _C = K8SConstants
        options = self._options = list()
        '''cluster name is our inventory_hostname unless override explicitly via cluster_name'''
        self._cluster_name = self._lookup_helper.resolve_var(_C.v_cluster_name, 
                                                            default=self._lookup_helper.resolve_var(_C.va_inv_host))
        options.append('--cluster={}'.format(self._cluster_name))
        kube_context = self._lookup_helper.resolve_var('kube_context', 
                                                        default=self._cluster_name)
        options.append('--context={}'.format(kube_context))

        kube_config = self._lookup_helper.resolve_var('kube_config', default=None)
        if kube_config is not None:
            kube_config = os.path.realpath(os.path.expandvars(os.path.expanduser(kube_config)))
            options.append('--kubeconfig={}'.format(kube_config))

        self._cmd = self._cmd.bake(*options)
        self.f_v("Starting kubectl version")
        start = timer()
        cmd_out = self._cmd("version", "-o", "yaml")
        end = timer()
        self.f_v("timer version_cmd: {}ms", timedelta(milliseconds=end-start).microseconds)
        version_info_rescs = list(filter(None, yaml.safe_load_all(cmd_out.stdout)))
        if len(version_info_rescs) != 1:
            #raise AnsibleAssertionError("kubectl version error:\n{}".format(pprint_to_yaml(version_info_rescs)))
            print("kubectl version error:\n{}".format(pprint_to_yaml(version_info_rescs)))
        client_version = version_info_rescs[0]['clientVersion']
        server_version = version_info_rescs[0]['serverVersion']
        if client_version['major'] != server_version['major']:
            #raise AnsibleAssertionError("kubectl and api-server MAJOR Version skew:\n{}".format(pprint_to_yaml(version_info_rescs)))
            print("kubectl and api-server MAJOR Version skew:\n{}".format(pprint_to_yaml(version_info_rescs)))
        client_minor = int(client_version['minor'])
        server_minor = int(server_version['minor'])

        if client_minor not in (server_minor - 1, server_minor, server_minor + 1):
            #raise AnsibleAssertionError("kubectl and api-server MINOR Version skew. Must be +- 1 or same as server minor version.\n{}".format(pprint_to_yaml(version_info_rescs)))
            print("kubectl and api-server MINOR Version skew. Must be +- 1 or same as server minor version.\n{}".format(pprint_to_yaml(version_info_rescs)))
        self.f_vvv("version_info_docs:\n{}", version_info_rescs[0])

    def execute(self, cmd, *cmd_args, **kwargs):
        """Execute the command"""
        check_for_sequence(cmd_args, "cmd_args")
        check_for_mapping(kwargs, "kwargs")
        self.f_v("Starting kubectl {}".format(cmd))
        start = timer()
        try:
            ''' Note Command returns an instance of sh.RunningCommand, also exit code 1 ok?'''
            cmd_run_obj = self._cmd(cmd, *cmd_args, **kwargs)
        except sh.ErrorReturnCode as e:
            raise AnsibleError("Failed to execute command: [{}]".format(to_native(e)), orig_exc=e)
        end = timer()
        self.f_v("timer get: {}ms", timedelta(milliseconds=end-start).microseconds)
        # HACK Alert, cmd_run_obj call_args is not publicly exposed. please watch
        # for changes
        encoding = cmd_run_obj.call_args['encoding']
        result = {
            'exit_code': cmd_run_obj.exit_code,
            'output': cmd_run_obj.stdout if six.PY2 else cmd_run_obj.stdout.decode(encoding),
            'stderr': cmd_run_obj.stderr if six.PY2 else cmd_run_obj.stderr.decode(encoding),
        }
        return result

    def apply(self, manifest_path):
        """Apply wrapper"""
        cmd_args = ['-f', manifest_path]
        result = self.execute('get', *cmd_args)
        return result

    def check(self, manifest_path):
        """diff wrapper"""
        cmd_args = ['-f', manifest_path]
        result = self.execute('diff', *cmd_args, _ok_code=[0,1])
        # calculate potential changes
        #TODO: diff_matches = KubectlCmd.diff_search_expr.findall(cmd_run_obj.stdout)
        return result

    def get(self, resc_name, kind, namespace=None):
        """kubectl get"""

        self.f_v("Starting kubectl get")
        cmd_args = [kind, resc_name, '--output=yaml']
        if namespace is not None:
            cmd_args.append('--namespace={}'.format(namespace))
        result = self._execute('get', *cmd_args)
        return result
