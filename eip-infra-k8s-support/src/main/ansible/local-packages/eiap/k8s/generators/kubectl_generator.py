# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import os
import yaml

from eiap.ansible.lookup import LookupHelper
from eiap.ansible.mixins.display import DisplayMixin
from eiap.commands import KubectlCmd
from eiap.k8s.path_vars import K8SPaths
from eiap.utils import (check_for_mapping, check_instance, check_for_sequence,
                        check_key, check_for_string,)
import six

class KubectlGenerator(DisplayMixin):
    """Singleton to generate secrets via kubectl command.

    IMPORTANT:
    - NO __init__ method, do the initialization in __new__
    """
    _INSTANCE = None

    def __new__(cls, lookup_helper):
        """create a instance of the API Manager"""
        check_instance(lookup_helper, LookupHelper, "SecretGenerator")
        if cls._INSTANCE is None:
            cls._INSTANCE  = instance = super(KubectlGenerator, cls).__new__(cls)
            # call __init__ in case any BaseClasses need it.
            super(cls, instance).__init__()
            # call the initialization code
            instance._initialize(lookup_helper)
        return cls._INSTANCE

    def _initialize(self, lookup_helper):
        self._lookup_helper = lookup_helper
        self._k8s_paths = K8SPaths(self._lookup_helper)
        self._kctl_cmd = KubectlCmd.create(lookup_helper, use_default_cmd=True)
        self._repr = None

    def generate(self, cmd_cfg, namespace):
        """Generate the secret from the provided config"""
        check_for_mapping(cmd_cfg, 'cmd_cfg')
        cmd_options = list()
        cmd_options.append('--namespace={}'.format(namespace))
        cmd_args = list()
        check_key('cmd', cmd_cfg, "sub-command")
        cmd_args.append(cmd_cfg['cmd'])
        cmd_type = cmd_cfg.get('cmd_type', None)
        if cmd_type is not None:
            cmd_args.append(cmd_cfg['cmd_type'])
        check_key('name', cmd_cfg, 'cmd_cfg')
        resc_name = cmd_cfg['name']
        cmd_args.append(resc_name)
        cmd_args_cfg = cmd_cfg.get('cmd_args', {})
        long_opts = cmd_args_cfg.get('long_opts', {})
        check_for_mapping(long_opts, 'long_opts')
        for arg, val in six.iteritems(long_opts):
            if arg == 'from-file':
                check_for_sequence(val, 'file_options')
                for _f in val:
                    check_for_mapping(_f, 'file_options: item')
                    fpath = self._k8s_paths.resolve_path(_f['file'], dir_prefix=None)
                    fkey = _f.get('key', os.path.basename(fpath))
                    cmd_args.append("--from-file={}={}".format(fkey, fpath))
            elif arg in ('from-env-file', 'cert', 'key'):
                if arg == 'from-env-file':
                    check_for_sequence(val, 'from-env-file')
                    values = val
                else:
                    # this can be a mapping (cert, keys)
                    check_for_mapping(val, arg)
                    values = [val]
                for _f in values:
                    check_for_mapping(_f, 'file_options: item')
                    fpath = self._k8s_paths.resolve_path(_f['file'], dir_prefix=None)
                    cmd_args.append("--{}={}".format(fpath))
            elif arg in ('from-literal',):
                check_for_mapping(val, 'from-literal')
                for k, v in six.iteritems(val):
                    check_for_string(v, "from-litral:v")
                    #TODO: support already b64 values?
                    cmd_args.append("--{}={}={}".format(arg, k, v))
            else:
                cmd_args.append("--{}={}".format(arg, val))
            #
        short_opts = cmd_args_cfg.get('short_opts', {})
        check_for_mapping(short_opts, 'short_opts')
        for arg, val in six.iteritems(short_opts):
            #TODO: we assume scalar values, maybe provide more sophisticated versions?
            cmd_args.append('-' + arg)
            cmd_args.append(val)

        cmd_args.append('--output=yaml')
        # MUST DO!
        cmd_args.append('--dry-run=client')
        combined_args = cmd_args + cmd_options
        result = self._kctl_cmd.execute('create', *combined_args)
        k8s_resc = yaml.safe_load(result['output'])
        self.f_vvvv("secret k8s_resc:\n{}", k8s_resc)
        return k8s_resc





