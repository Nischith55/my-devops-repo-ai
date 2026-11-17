# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import os

from ansible.errors import AnsibleAssertionError

from eiap.ansible.helpers import pprint_to_yaml, NoAliasAnsibleDumper
from eiap.ansible.lookup import LookupHelper
from eiap.ansible.mixins.display import DisplayMixin
from eiap.constants import K8SConstants
from eiap.utils import (check_instance, check_for_sequence, check_for_string)
from eiap.mixins import MappingMixin


class K8SPaths(DisplayMixin, MappingMixin):
    """Class that encapsulates all paths for k8s-support playbooks. NOTE: this is
    a singleton.

    NOTES:
    - no __init__ method should be implemented all initialization should be done
    in __new__
    - 
    """
    _instance = None

    def __new__(cls, lookup_helper):
        """We use new method to instantiate a single instance of this class"""
        if cls._instance is None:
            cls._instance  = instance = super(K8SPaths, cls).__new__(cls)
            # call the initialization code
            # call __init__ in case any BaseClasses need it.
            super(cls, instance).__init__()
            _C = K8SConstants
            check_instance(lookup_helper, LookupHelper, "K8SPaths")
            instance._lookup_helper = lookup_helper
            # allow override through CLI
            src_ndots = lookup_helper.resolve_var('src_ndots', default=5)
            instance._data = dict()
            instance._repr = None
            '''cluster name is our inventory_hostname unless override explicitly via cluster_name'''
            instance._cluster_name = instance._data['cluster_name'] = instance._lookup_helper.resolve_var(_C.v_cluster_name, 
                                                                                               default=instance._lookup_helper.resolve_var(_C.va_inv_host))
            base_paths = instance._build_paths(src_ndots)
            instance._data.update(base_paths)
        return K8SPaths._instance

    def _build_paths(self, src_ndots):
        """Build the paths required for running the playbooks"""
        lookup_helper = self._lookup_helper
        data = dict()
        _C = K8SConstants
        playbook_dir = lookup_helper.resolve_var(_C.va_playbook_dir)
        src_root = os.path.join(playbook_dir, *(['..'] * src_ndots))
        src_root_dir = os.path.realpath(os.path.expandvars(os.path.expanduser(src_root)))
        '''override from cli'''
        src_root_dir = lookup_helper.resolve_var(_C.v_src_root_dir, default=src_root_dir)
        src_main_dir = os.path.join(src_root_dir, 'src', 'main')
        data['target_dir'] = os.path.realpath(os.path.join(src_root_dir, 'target'))
        env = lookup_helper.resolve_var('env')
        dept = lookup_helper.resolve_var('dept')
        data['inventory_env_dir'] = os.path.realpath(os.path.expandvars(os.path.expanduser(
                        os.path.join(src_main_dir, 'ansible', 'inventory', 'k8s', dept, env))
                      ))
        k8s_root_dir = os.path.realpath(os.path.expandvars(os.path.expanduser(
                        os.path.join(src_main_dir, 'k8s'))
                      ))
        data['k8s_root_dir'] = k8s_root_dir
        data['certs_root_dir'] = os.path.realpath(os.path.expandvars(os.path.expanduser(
                        os.path.join(src_main_dir, 'certs'))
                      ))
        data['default_env_dir'] = os.path.realpath(os.path.expandvars(os.path.expanduser(
                        os.path.join(src_main_dir, 'ansible', 'inventory', 'k8s'))
                      ))
        data['storage_builtin_dir'] = os.path.realpath(os.path.expandvars(os.path.expanduser(
                        os.path.join(data['default_env_dir'], 'defaults', 'group_vars', 'cluster_config', 'storage'))
                      ))
        data['storage_all_dir'] = os.path.realpath(os.path.expandvars(os.path.expanduser(
                        os.path.join(data['default_env_dir'], dept, env, 'host_vars', self._cluster_name, 'storage-classes'))
                      ))
        data['add_ons_base_dir'] = os.path.realpath(os.path.join(k8s_root_dir, 'add-ons'))
        data['global_kustomize_base_dir'] = os.path.realpath(os.path.join(k8s_root_dir, 'kustomize'))
        data['apps_base_dir'] = os.path.realpath(os.path.join(k8s_root_dir, 'apps'))
        deploy_base_dir = data['deployments_base_dir'] = os.path.realpath(os.path.join(k8s_root_dir, 'deployments'))
        data['templates_base_dir'] = os.path.realpath(os.path.join(playbook_dir, 'templates'))
        data['deployments_root_dir'] = os.path.realpath(os.path.join(deploy_base_dir, dept, env, self._cluster_name))
        data['overlays_root_dir'] = os.path.realpath(os.path.join(data['target_dir'], dept, env, self._cluster_name))
        # secret manifest root dir is same as overlays root dir
        data['secret_manifest_root_dir'] = os.path.realpath(os.path.join(deploy_base_dir, dept, env, self._cluster_name))

        return data

    def resolve_path(self, path_str, dir_prefix=None):
        """calculate the fullpath based on path string with well known tokens"""
        check_for_string(path_str, "partial")
        if path_str.startswith("/"):
            return path_str
        token, delim, remain = path_str.partition(':')
        if remain.startswith("/"):
            return remain
        # if delim empty just parse remain, as it has to relative to genreator
        if delim == '':
            return os.path.join(dir_prefix if dir_prefix is not None else dir_prefix, path_str)
        if token == 'kustomize_root':
            return os.path.join(self.global_kustomize_base_dir, remain)
        elif token == 'certs_root':
            return os.path.join(self.certs_root_dir, remain)
        raise AnsibleAssertionError("Unsupported token: [{}]".format(token))

    def search_path_kustomize(self, prefix_dir, app_name, filename):
        """search the built-in seacrh path based on well know locations for files or templates
        used in kustomize patches.
        """
        search_path = (
            os.path.join(self._data['add_ons_base_dir'], app_name, prefix_dir),
            os.path.join(self._data['apps_base_dir'], app_name, prefix_dir),
            os.path.join(self._data['add_ons_base_dir'], prefix_dir),
            os.path.join(self._data['apps_base_dir'], prefix_dir),
            os.path.join(self._data['k8s_root_dir'], 'kustomize', prefix_dir),
        )
        return self.search_path(search_path, filename)

    def search_path(self, search_path, filename):
        """Given the search path get the last match in the path"""
        check_for_sequence(search_path, "search_path")
        if filename.startswith("/"):
            return filename
        for _p in search_path:
            candidate = os.path.join(_p, filename)
            if os.path.exists(candidate):
                return candidate
        raise AnsibleAssertionError("Could not find [{}] in search path: [{}]".format(filename, search_path))

    def search_path_depth_first(self, base_dir, search_path, filename):
        """
        """
        check_for_string(base_dir, "base_dir")
        check_for_string(search_path, "search_path")
        check_for_string(filename, "filename")
        assert base_dir.startswith("/")
        assert not search_path.startswith(os.sep)
        assert not filename.startswith(os.sep)
        path_list = list()
        _path = ''
        search_path_components = filter(None, os.path.normpath(search_path).split(os.sep))
        for _p in search_path_components:
            _path = os.path.join(_path, _p)
            path_list.append(os.path.join(base_dir, _path, filename))
        path_list.reverse()
        self.f_vv("path_list:\n{}", path_list)
        filepath = None
        for _p in path_list:
            if os.path.exists(_p):
                filepath = _p
                break
        self.f_v("locating file [{}]: fullpath is: [{}]", filename, filepath)
        return filepath

    def resc_dirpath_format(self, resc_abbrev): 
        """Get the resource kind directory where the resource manifest will be saved

        IMPORTANT:
            - returns a format string. with resc_name, resc_namespace both optional
              format variables
        """
        _C = K8SConstants
        if resc_abbrev not in self._resc_paths:
            raise AnsibleAssertionError("Resource abbreviation: [{}] is not part of specification".format(resc_abbrev))
        path = self._resc_paths[resc_abbrev][_C.k_manifest_dir_fmt]
        return path

    @property
    def data(self):
        return self._data

    @property
    def repr(self):
        if self._repr is None:
            self._repr = "{}".format(pprint_to_yaml(self.data))
        return self._repr

    @property
    def certs_root_dir(self):
        return self._data['certs_root_dir']

    @property
    def role_ref_dir(self):
        return self._data['role_ref_dir']

    @property
    def global_kustomize_base_dir(self):
        return self._data['global_kustomize_base_dir']

    @property
    def add_ons_base_dir(self):
        return self._data['add_ons_base_dir']

    @property
    def apps_base_dir(self):
        return self._data['apps_base_dir']

    @property
    def deploy_root_dir(self):
        return self._data['deployments_root_dir']

    @property
    def overlays_root_dir(self):
        return self._data['overlays_root_dir']

    @property
    def secret_manifest_root_dir(self):
        return self._data['secret_manifest_root_dir']

    @property
    def cluster_name(self):
        return self._cluster_name

    @property
    def params(self):
        """get the params"""
        return self._data

# ## Add it to our representer
NoAliasAnsibleDumper.add_representer(
    K8SPaths,
    K8SPaths.yaml_representer
)
