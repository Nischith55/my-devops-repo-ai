# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
import sys
import abc
import os
import six
import yaml
import glob
import jinja2
import re
import ast
from pathlib import Path

from ansible.errors import (AnsibleAssertionError, AnsibleError, )

from copy import deepcopy

from eiap.utils import (check_instance, check_for_string, check_for_sequence,)
from eiap.ansible.lookup import LookupHelper
from eiap.ansible.mixins.display import DisplayMixin
from eiap.commands import (KubectlCmd, KustomizeCmd, )
from eiap.constants import K8SConstants
from eiap.k8s.api import K8SApiManager
from eiap.ansible.helpers import pprint_to_yaml
from eiap.k8s.path_vars import K8SPaths
from eiap.k8s.resource import (KustomizeResourceDefintion, K8SResourceDefintion)
from eiap.k8s.settings import AppSettings
from eiap.ansible.helpers import read_yaml_all
from jinja2 import Environment, FileSystemLoader
from ansible.template import Templar

@six.add_metaclass(abc.ABCMeta)
class TaskHandler(DisplayMixin):
    """Abstract class to handle the different variations of handling tasks
    in kubernetes cluster.
    """

    KCTL_ACTION_CMD = {
        'apply': {
            'cmd': 'apply',
            'args': (
                '-o',
                'yaml',
            ),
            'kwargs': {
                '_ok_code': (0,),
            }
        },
        
        'update': {
            'cmd': 'apply',
            'args': (
                '-o',
                'yaml',
            ),
            'kwargs': {
                '_ok_code': (0,),
            }
        },

        'replace': {
            'cmd': 'replace',
            'args': (
                '-o',
                'yaml',
                '--force',
            ),
            'kwargs': {
                '_ok_code': (0,),
            }
        },

 
        'diff': {
            'cmd': 'diff',
            'kwargs': {
                '_ok_code': (0, 1),
            }
        },

        'info': {
            'cmd': 'get',
            'args': (
                '-o',
                'yaml',
            ),
            'kwargs': {
                '_ok_code': (0,),
            }
        },

        'write': {
            'cmd': 'get',
            'args': (
                '-o',
                'yaml',
            ),
            'kwargs': {
                '_ok_code': (0,),
            }
        },
    }

    SUPPORTED_TASK_ENTITIES = (
        'add_on',
        'app',
        'resc',
        'kctl',
    )

    @staticmethod
    def parse_task_str(task_str):
        """Parse a task_str.

        NOTES:
        - task_str consists of <action>_<optional_keyword>_<entity>
        """
        check_for_string(task_str, "task_str")
        _d = DisplayMixin()
        _C = K8SConstants
        '''partition from left'''
        task_parts = task_str.partition(_C.delim)
        if task_parts[1] == '':
            raise AnsibleAssertionError("Illegal task_str: [{}], format should be <action>_<..>".format(task_str))
        '''action is always first'''
        action = task_parts[0]
        remain_task_str = task_parts[2]
        _d.f_v("task_str: [{}] :: action: [{}], remaining task_str: [{}]".format(task_str, action, remain_task_str))
        if not remain_task_str.endswith(TaskHandler.SUPPORTED_TASK_ENTITIES):
            raise AnsibleAssertionError("'task_str', must endwith _{}".format(TaskHandler.SUPPORTED_TASK_ENTITIES))
        return (action, remain_task_str)

    @classmethod
    def create_from_task_str(cls, lookup_helper, task_str, **task_args):
        check_instance(lookup_helper, LookupHelper, "TaskHandler")
        action, remain_task_str = TaskHandler.parse_task_str(task_str)
        task_handler = None
        if remain_task_str.startswith('add_on') or remain_task_str.startswith('app'):
            task_handler = AppTaskHandler(lookup_helper, action, remain_task_str, **task_args)
        elif remain_task_str.endswith('resc'):
            task_handler = ResourceTaskHandler(lookup_helper, action, remain_task_str, **task_args)
        else:
            # TODO:
            raise AnsibleError("Unsupported task: [{}]".format(remain_task_str))
        return task_handler

    def __init__(self, lookup_helper, **task_args):
        super(TaskHandler, self).__init__()
        check_instance(lookup_helper, LookupHelper, "TaskHandler")
        '''only shared variables'''
        self._lookup_helper = lookup_helper
        # additional task_args from action module
        self._task_args = task_args
        self._k8s_paths = K8SPaths(lookup_helper)
        self._kctl_cmd = KubectlCmd.create(self._lookup_helper, use_default_cmd=True)
        # NOTE: this variables should already exist (see k8s_tasks.py in plugins/action module)
        # _check_mode_ == --check
        self._check_mode = lookup_helper.resolve_var("_check_mode_")
        # _diff_mode_ == --diff
        self._diff_mode = lookup_helper.resolve_var("_diff_mode_")
        skip_kctl = lookup_helper.resolve_var("skip_kctl", default=True)
        # NOTE: if in diff mode force skip_kctl to False
        self._skip_kctl = False if self._diff_mode else skip_kctl
        self._skip_kustomize = lookup_helper.resolve_var("skip_kustomize", default=False)
        self._skip_generate = lookup_helper.resolve_var("skip_generate", default=False)
        self._sa_rb = lookup_helper.resolve_var("sa_rb", default=False)

    def _read_all_k8s_resources(self, manifest_dir):
        """read all manifests from the dir, no recursion allowed"""
        k8s_resc_files = [os.path.join(manifest_dir, _) for _ in os.listdir(manifest_dir) if _.endswith(('.yml', '.yaml'))]
        k8s_rescs = list()
        for k8s_file in k8s_resc_files:
            _k8s_rescs = read_yaml_all(k8s_file)
            if len(_k8s_rescs) == 1:
                _k8s_rescs[0]['manifest_path'] = k8s_file
            elif len(_k8s_rescs) > 1:
                for _r in _k8s_rescs:
                    _r['manifest_dir'] = manifest_dir
            k8s_rescs.extend(_k8s_rescs)
        #
        # IMPORTANT: This will added our labels and annotations (post process)
        # - sorting is a MUST so we process a set of manifests in order. See K8SResourceDefinition
        
        k8s_resc_objs = sorted([K8SResourceDefintion(self._lookup_helper, k8s_resc) for k8s_resc in k8s_rescs])
        return k8s_resc_objs

    def _build_kctl_cmd_args(self, action, additional_cmd_args):
        """build the command args default and any cli overrides before passing to the kubectl command"""
        ret = []
        # command args first get the default for the actions
        # then any overrides <action>_args
        ret.extend(list(deepcopy(self.KCTL_ACTION_CMD[action].get('args', []))))
        if additional_cmd_args is not None:
            check_for_sequence(additional_cmd_args, 'additional_cmd_args')
            ret.extend(deepcopy(additional_cmd_args))
        #cli command args
        cmd_args_cli = self._lookup_helper.resolve_var(action + '_args', default=[])
        check_for_sequence(cmd_args_cli, 'cmd_args_cli')
        ret.extend(cmd_args_cli)
        return ret

    def do_kctl_cmd_name(self, action, api_def, resc_names, resc_namespace=None, additional_cmd_args=None):
        """Issue kctl_command by name"""
        check_for_sequence(resc_names, 'resc_names')
        ret = list()
        cmd = self.KCTL_ACTION_CMD[action]['cmd']
        kwargs = self.KCTL_ACTION_CMD[action].get('kwargs', {})
        # build the command arguments
        cmd_args = self._build_kctl_cmd_args(action, additional_cmd_args)
        if resc_namespace is not None:
            cmd_args.append('--namespace={}'.format(resc_namespace))
        self.f_console("cmd_args: {}", cmd_args)
        for _r in resc_names:
            result = self._kctl_cmd.execute(cmd, api_def.name, _r, *cmd_args, **kwargs)
            ret.append(result)
        # empty resc_names => all
        if not resc_names:
            result = self._kctl_cmd.execute(cmd, api_def.name, *cmd_args, **kwargs)
            ret.append(result)
        return ret

    def do_kctl_cmd(self, action, manifest_dir=None, k8s_objs=None, additional_cmd_args=None):
        """This method should be called when a whole lot of manifests (typically add-ons or apps)
        need to be applied or created.

        NOTES:
        - manifest_dir and k8s_objs are mutually exclusive.
        - any last minute adjustments can be done here such as providing defaults etc.

        """
        if manifest_dir is not None and k8s_objs is not None:
            raise AnsibleAssertionError("do_kctl_cmd:: both 'mainfest_dir' and 'k8s_objs' specified. mutually excluseive")
        ret = list()
        if manifest_dir is not None:
            k8s_objs = list()
            check_for_string(manifest_dir, "manifest_dir")
            k8s_objs.extend(self._read_all_k8s_resources(manifest_dir))
        # make sure k8s_objs exist
        check_for_sequence(k8s_objs, 'k8s_objs')
        if len(k8s_objs) == 0:
            raise AnsibleAssertionError("no 'k8s_objs' found either a manifest_dir or k8s_obj must exist.")
        cmd = self.KCTL_ACTION_CMD[action]['cmd']
        changed = True
        if cmd in ('diff', 'info'):
            changed = False
        kwargs = self.KCTL_ACTION_CMD[action].get('kwargs', {})
        # build the command arguments
        cmd_args = self._build_kctl_cmd_args(action, additional_cmd_args)
        for k8s_obj in k8s_objs:
            result = self._kctl_cmd.execute(cmd, '-f', '-',  _in=str(k8s_obj), *cmd_args, **kwargs)
            k8s_obj.update_result(changed=changed, **result)
            ret.append(k8s_obj.result)
        return ret

    def do_kctl_cmd_single_resc(self, action, manifest_path, resc_namespace, additional_cmd_args=None):
        ret = list()
        cmd = self.KCTL_ACTION_CMD[action]['cmd']
        kwargs = self.KCTL_ACTION_CMD[action].get('kwargs', {})
        cmd_args = self._build_kctl_cmd_args(action, additional_cmd_args)
        if resc_namespace is not None:
            cmd_args.append('--namespace={}'.format(resc_namespace))
        result = self._kctl_cmd.execute(cmd, '-f', manifest_path, *cmd_args, **kwargs)
        ret.append(result)
        return ret

    

    @abc.abstractproperty
    def supported_actions(self):
        """property to return a list of supported actions"""
        pass

    @abc.abstractmethod
    def execute_task(self, action, **task_args): # @UnusedVariable
        """NOTE: subclass should call this method via super"""
        # first thing first, ensure we have a valid action
        if not self._check_mode or not self._diff_mode:
            if action not in self.supported_actions():
                raise AnsibleError("action [{}] not supported. Valid actions: {}".format(action, self.supported_actions))

class AppTaskHandler(TaskHandler):
    """Generic App or Add-on task handler"""

    def __init__(self, lookup_helper, action, remain_task_str, **task_args):
        super(AppTaskHandler, self).__init__(lookup_helper, **task_args)
        check_for_string(action, 'action')
        try:
            app_name = self._lookup_helper.resolve_var('app_name')
        except Exception as e:
            raise AnsibleAssertionError("[app_name] is required for 'add_on' or 'app' task. [{}]".format(e.message), orig_exc=e)
        check_for_string(app_name, 'app_name')
        self._name = app_name
        is_add_on = True if remain_task_str.startswith('add_on') else False
        self._app_settings = AppSettings.create_app_settings(lookup_helper, is_add_on, app_name)
        self._action = action

    # BEGIN: Abstract methods/properties for TaskHandler

    def supported_actions(self):
        """abstract property implementation"""
        # we do not implement write for AppTaskHandler
        return ('apply', 'diff', 'info', )

    def execute_task(self):
        """Handle add_on or app tasks"""
        kctl_action = 'diff' if self._diff_mode else self._action
        super(AppTaskHandler, self).execute_task(kctl_action)
        ret = list()
        # no point in proceeding further if all three skips are present
        if self._skip_generate and self._skip_kustomize and self._skip_kctl:
            ret.append({
                'skipped': True,
                'skip_generate': self._skip_generate,
                'skip_kustomize': self._skip_kustomize,
                'skip_kctl': self._skip_kctl,
            })
            return ret

        try:
            instance_name = self._lookup_helper.resolve_var('instance')
        except Exception as e:
            raise AnsibleAssertionError("'instance' is required for app: [{}]. {}".format(self._name, e.message), orig_exc=e)
        # locate settings
        component_name = self._lookup_helper.resolve_var('component', default=None)
        settings = self._app_settings.get_settings(instance_name, component_name)
        self.f_vv("Settings:\n{}", settings)
        if not self._skip_generate:
            kustomize_resc = KustomizeResourceDefintion(self._lookup_helper, settings)
            kustomize_resc.save(generated='kustomize_resc_def')
            ret.append(kustomize_resc.result)
        k8s_resc_objs = None
        if not self._skip_kustomize:
            kustomize_cmd = KustomizeCmd.create(self._lookup_helper, use_default_cmd=True)
            k8s_rescs = kustomize_cmd.build(settings.overlays_dir)
            # IMPORTANT: This will added our labels and annotations (post process)
            k8s_resc_objs = sorted([K8SResourceDefintion(self._lookup_helper, k8s_resc, manifest_dir=settings.manifests_dir) \
                                    for k8s_resc in k8s_rescs])
            self.f_vv("k8s_resc_objs:\n{}", k8s_resc_objs)
            # save the manifests before apply
            for k8s_resc_obj in k8s_resc_objs:
                k8s_resc_obj.save(generated='kustomize_build')
                ret.append(k8s_resc_obj.result)

        if not self._skip_kctl and not self._check_mode:
            kwargs = dict()
            if k8s_resc_objs is not None:
                kwargs['k8s_objs'] = k8s_resc_objs
            else:
                kwargs['manifest_dir'] = settings.manifests_dir
            results = self.do_kctl_cmd(kctl_action, **kwargs)
            ret.extend(results)
        return ret

    @property
    def app_name(self):
        return self._app_name

    @property
    def app_base_dir(self):
        return self._app_base_dir

    @property
    def app_deploy_base_dir(self):
        return self._app_deploy_base_dir

class ResourceTaskHandler(TaskHandler):
    """Generic App or Add-on task handler"""

    ALLOWED_SUB_ACTION = (
        '',
        'all',
        'builtin',
    )

    def __init__(self, lookup_helper, action, remain_task_str, **task_args):
        super(ResourceTaskHandler, self).__init__(lookup_helper, **task_args)
        check_for_string(action, "action")
        check_for_string(remain_task_str, "remain_task_str")
        self._lookup_helper = lookup_helper
        # singleton safe
        self._k8s_api_mgr = K8SApiManager(lookup_helper)
        self._action = action
        # partition (right) (first one)
        self._sub_action = remain_task_str.rpartition('_resc')[0]
        if self._sub_action not in self.ALLOWED_SUB_ACTION:
            raise AnsibleAssertionError("task sub action, allowed values are: {}".format(self.ALLOWED_SUB_ACTION))
        # we need resource kind
        resc_kind_or_name = self._lookup_helper.resolve_var('resc_kind', default=None)
        if resc_kind_or_name is None:
            raise AnsibleAssertionError("either 'resc_kind' which can be k8s api 'Kind' or 'Name' or 'short_name'")
        self._k8s_resc_api_def = self._k8s_api_mgr.get_resource_api_kind_or_name(resc_kind_or_name)
        self._resc_kind = self._k8s_resc_api_def.kind
        self._resc_apigroup = self._k8s_resc_api_def.group
        self._resc_version = self._k8s_resc_api_def.api_version
        self._resc_short_name = self._k8s_resc_api_def.short_name
        self.f_v("resc api def:\n{}", self._k8s_resc_api_def)

        self._subjects = self._lookup_helper.resolve_var(K8SConstants.v_subjects)
        self.f_vv("subjects:\n{}", self._subjects)
        self.subject_dict = dict(self._subjects)
        
        self._role_ref = self._lookup_helper.resolve_var(K8SConstants.v_role_ref)
        self.f_vv("role reference:\n{}", self._role_ref)
        
        

        self._resc_names = list()
        self._cmd_args = list()

        self._dict = dict()
        self._dict['k8s_paths'] = self._k8s_paths


 
        resc_name = self._lookup_helper.resolve_var('resc_name', default=None)
        resc_namespace = self._lookup_helper.resolve_var('resc_namespace', default=None)
        if resc_name is not None:
            self._resc_names.append(resc_name)
        self._resc_namespace = self._lookup_helper.resolve_var('resc_namespace', default=None)
        if self._resc_namespace is None and (self._k8s_resc_api_def.namespaced and not self._sub_action == 'all'):
            raise AnsibleAssertionError("'resc_namespace' is required for resource kind: {}".format(self._resc_kind))

        # validate subactions
        self._validate_subactions(self._resc_names, self._resc_namespace)
        
        if self._action in ('info', 'diff',):
            # if all and no namespace provided get all namespaces
            if self._k8s_resc_api_def.namespaced and self._resc_namespace is None:
                self._cmd_args.append("-A")

    def _validate_subactions(self, resc_names, resc_namespace): # @UnusedVariable (resc_namespace)
        """Validate the subactions"""
        if self._sub_action == '' and len(resc_names) != 1:
            # make sure we have at least 1 resource
            raise AnsibleAssertionError("'resc_name' is required. self._resc_names: {}".format(resc_names))
        elif self._sub_action == 'all':
            if len(resc_names) > 0:
                raise AnsibleAssertionError("'all' subaction should not specify 'resc_name' ")

        elif self._sub_action == 'builtin':
            if len(resc_names) > 0:
                raise AnsibleAssertionError("'builtin' subaction should not specify 'resc_name' ")


    def _check_resource(self, resc_api_def, resc_name, resc_namespace):
        """Check the resource if it exists before allowing apply action"""
        cmd_args = ['--ignore-not-found', '-o', 'yaml']
        if resc_api_def.namespaced:
            cmd_args.extend(['-n', resc_namespace])
        result = self._kctl_cmd.execute('get', self._k8s_resc_api_def.name, resc_name, *cmd_args)
        resc_yaml = yaml.safe_load(result['output'])
        self.f_vvv("resource:\n {}", resc_yaml)
        return resc_yaml


    def _read_storageclass_config_file(self, **kwargs):
        ret1 = []
        kctl_action = 'diff' if self._diff_mode else self._action
        if self._sub_action == 'builtin':
            path = self._dict['k8s_paths']['storage_builtin_dir']
            text_files = glob.glob(path + "/**/*.yml", recursive = True)
            for filename in text_files:
                with open(filename) as f:
                    file_contents = f.read()
                    for match in re.findall(r'\bpep_eiap\w+_sto_class_built_in\b',file_contents, re.I):
                        sc_conf = self._lookup_helper.resolve_var(match)
                        test_dict = {}
                        test_dict = sc_conf
                        file_yaml_name = test_dict['metadata']['name']
                        test_dict['kind'] = self._resc_kind
                        test_dict['apiVersion'] = self._resc_version
                        resc_new_yaml = pprint_to_yaml(test_dict)
                        resc_yaml = yaml.safe_load(resc_new_yaml)
                        k8s_obj = K8SResourceDefintion(self._lookup_helper, resc_yaml, filter_keys=False)
                        skip_save = self._lookup_helper.resolve_var('skip_save', False)
                        if not skip_save:
                            k8s_obj.save()
                        ret1.append(k8s_obj.result)
                        self.f_v("k8s_obj:\n{}", k8s_obj)
        elif self._sub_action == 'all':
            path = self._dict['k8s_paths']['storage_all_dir']
            text_files = glob.glob(path + "/**/*.yml", recursive = True)
            for filename in text_files:
                with open(filename) as f:
                    file_contents = f.read()
                    for match in re.findall(r'\b__custom_storage_class_params__\b',file_contents, re.I):
                        sc_params_config = self._lookup_helper.resolve_var(match)
                        sc_params = {}
                        sc_params = sc_params_config
                        PROVISIONERS = {
                        'disk': 'kubernetes.io/azure-disk',
                        'file': 'kubernetes.io/azure-file',
                        }
                        TMPL_VARNAME = '__azure_storage_class_template__'        
                        TMPL_PARAMS_VARNAME = '__tmpl_params__'
                        tmpl_var = kwargs.get('template_varname', TMPL_VARNAME)
                        tmpl_params_varname = kwargs.get('template_params_varname', TMPL_PARAMS_VARNAME)
                        tmpl_raw = {}
                        tmpl_raw = self._lookup_helper.get_var_raw(tmpl_var , default=None)
                        sc_types = PROVISIONERS
                        for name, params in sc_params.items():
                            _tmpl_params = deepcopy(params)
                            if 'provisioner' not in params:
                                sc_t = params.get('type', None)
                                if sc_t not in sc_types:
                                    raise AnsibleAssertionError("storage class type {0} invalid, supproted values are [{1}]".format(sc_t, sc_types.keys()))
                                _tmpl_params['provisioner'] = sc_types[sc_t]
                            _my_dict = {}
                            _my_dict['name'] = name
                            _tmpl_params['kind'] = self._resc_kind
                            _tmpl_params['apiVersion'] = self._resc_version
                            _tmpl_params['metadata'] = _my_dict
                            _tmpl_params.pop('type', None)
                            _tmpl_params.pop('name', None)
                            resc_new_yaml = pprint_to_yaml(_tmpl_params)
                            resc_yaml = yaml.safe_load(resc_new_yaml)
                            k8s_obj = K8SResourceDefintion(self._lookup_helper, resc_yaml, filter_keys=False)
                            skip_save = self._lookup_helper.resolve_var('skip_save', False)
                            if not skip_save:
                                k8s_obj.save()
                            ret1.append(k8s_obj.result)
                            self.f_v("k8s_obj:\n{}", k8s_obj)                
        return ret1

    def _apply_all_custom_namespace_create(self):
        ret1 = []
        ns_conf = self._lookup_helper.resolve_var('__all_ns__')
        for ns in ns_conf:
            mydict = {}
            test_dict = {}
            config = self._lookup_helper.resolve_var(ns)
            mydict['kind'] = self._resc_kind
            mydict['apiVersion'] = self._resc_version
            test_dict['name'] = config['name']
            if 'labels' in config:
                test_dict['labels'] = config['labels']
            mydict['metadata'] = test_dict
            resc_new_yaml = pprint_to_yaml(mydict)
            resc_yaml = yaml.safe_load(resc_new_yaml)
            k8s_obj = K8SResourceDefintion(self._lookup_helper, resc_yaml, filter_keys=False)
            ret1.append(k8s_obj.result)
            self.f_v("k8s_obj:\n{}", k8s_obj)
        return ret1

    def _read_all_custom_namespace_create(self):
        ret1 = []
        ns_conf = self._lookup_helper.resolve_var('__all_ns__')
        for ns in ns_conf:
            mydict = {}
            test_dict = {}
            config = self._lookup_helper.resolve_var(ns)
            mydict['kind'] = self._resc_kind
            mydict['apiVersion'] = self._resc_version
            test_dict['name'] = config['name']
            if 'labels' in config:
                test_dict['labels'] = config['labels']
            mydict['metadata'] = test_dict
            resc_new_yaml = pprint_to_yaml(mydict)
            resc_yaml = yaml.safe_load(resc_new_yaml)
            k8s_obj = K8SResourceDefintion(self._lookup_helper, resc_yaml, filter_keys=False)
            skip_save = self._lookup_helper.resolve_var('skip_save', False)
            if not skip_save:
                k8s_obj.save()
            ret1.append(k8s_obj.result)
            self.f_v("k8s_obj:\n{}", k8s_obj)
        return ret1

    def _read_storageclass_config_file_path(self, **kwargs):
        ret1 = []
        kctl_action = 'diff' if self._diff_mode else self._action
        if self._sub_action == 'builtin':
            path = self._dict['k8s_paths']['storage_builtin_dir']
            text_files = glob.glob(path + "/**/*.yml", recursive = True)
            for filename in text_files:
                with open(filename) as f:
                    file_contents = f.read()
                    for match in re.findall(r'\bpep_eiap\w+_sto_class_built_in\b',file_contents, re.I):
                        sc_conf = self._lookup_helper.resolve_var(match)
                        test_dict = {}
                        test_dict = sc_conf
                        file_yaml_name = test_dict['metadata']['name']
                        test_dict['kind'] = self._resc_kind
                        test_dict['apiVersion'] = self._resc_version
                        resc_new_yaml = pprint_to_yaml(test_dict)
                        resc_yaml = yaml.safe_load(resc_new_yaml)
                        k8s_obj = K8SResourceDefintion(self._lookup_helper, resc_yaml, filter_keys=False)
                        ret1.append(k8s_obj.result)
                        self.f_v("k8s_obj:\n{}", k8s_obj)
        elif self._sub_action == 'all':
            path = self._dict['k8s_paths']['storage_all_dir']
            text_files = glob.glob(path + "/**/*.yml", recursive = True)
            for filename in text_files:
                with open(filename) as f:
                    file_contents = f.read()
                    for match in re.findall(r'\b__custom_storage_class_params__\b',file_contents, re.I):
                        sc_params_config = self._lookup_helper.resolve_var(match)
                        sc_params = {}
                        sc_params = sc_params_config
                        PROVISIONERS = {
                        'disk': 'kubernetes.io/azure-disk',
                        'file': 'kubernetes.io/azure-file',
                        }
                        TMPL_VARNAME = '__azure_storage_class_template__'        
                        TMPL_PARAMS_VARNAME = '__tmpl_params__'
                        tmpl_var = kwargs.get('template_varname', TMPL_VARNAME)
                        tmpl_params_varname = kwargs.get('template_params_varname', TMPL_PARAMS_VARNAME)
                        tmpl_raw = {}
                        tmpl_raw = self._lookup_helper.get_var_raw(tmpl_var , default=None)
                        sc_types = PROVISIONERS
                        for name, params in sc_params.items():
                            _tmpl_params = deepcopy(params)
                            if 'provisioner' not in params:
                                sc_t = params.get('type', None)
                                if sc_t not in sc_types:
                                    raise AnsibleAssertionError("storage class type {0} invalid, supproted values are [{1}]".format(sc_t, sc_types.keys()))
                                _tmpl_params['provisioner'] = sc_types[sc_t]
                            _my_dict = {}
                            _my_dict['name'] = name
                            _tmpl_params['kind'] = self._resc_kind
                            _tmpl_params['apiVersion'] = self._resc_version
                            _tmpl_params['metadata'] = _my_dict
                            _tmpl_params.pop('type', None)
                            _tmpl_params.pop('name', None)
                            resc_new_yaml = pprint_to_yaml(_tmpl_params)
                            resc_yaml = yaml.safe_load(resc_new_yaml)
                            k8s_obj = K8SResourceDefintion(self._lookup_helper, resc_yaml, filter_keys=False)
                            ret1.append(k8s_obj.result)
                            self.f_v("k8s_obj:\n{}", k8s_obj)                
        return ret1

    def _read_config_file(self, new_resc_name):
        resc_name = self._lookup_helper.resolve_var('resc_name', default=None)
        sa_rb = self._lookup_helper.resolve_var('sa_rb', default=False)
        resc_kind = self._lookup_helper.resolve_var('resc_kind', default=None)
        resc_namespace = self._lookup_helper.resolve_var('resc_namespace', default=None)
        yaml_dict = self._lookup_helper.resolve_var(new_resc_name , default=None)
        test_dict = {}
        test1_dict = {}
        my_dict = {}
        if resc_kind == 'namespace':                            
            test_dict['name'] = yaml_dict['name']
            test_dict['labels'] = yaml_dict['labels']
            my_dict['metadata'] = test_dict
            my_dict['kind'] = self._resc_kind
            my_dict['apiVersion'] = self._resc_version
        elif resc_kind == 'rolebinding':
            test = yaml_dict['role_bindings']
            test1 = yaml_dict['service_accounts']
            res = [d for d in test if d['name'] == resc_name]
            for e in test1:
                if "role_bindings" in e:
                    l = e['role_bindings']
                    res1 = [temp for temp in l if temp['name'] == resc_name]
                else:
                    res1 = []
            if len(res) != 0 and len(res1) == 0:
                test_dict['name'] = resc_name
                test_dict['namespace'] = resc_namespace
                my_dict['metadata'] = test_dict
                my_dict['kind'] = self._resc_kind
                my_dict['apiVersion'] = self._resc_version
                my_dict['subjects'] = res[0]['subjects']
                my_dict['roleRef'] = res[0]['roleref']    
            elif len(res1) != 0 and len(res) == 0:
                test1_dict['kind'] = 'ServiceAccount'
                test1_dict['apiGroup'] = ""
                test1_dict['namespace'] = resc_namespace
                test1_dict['name'] = test1[0]['name']
                test_dict['name'] = resc_name
                test_dict['namespace'] = resc_namespace
                my_dict['metadata'] = test_dict
                my_dict['kind'] = self._resc_kind
                my_dict['apiVersion'] = self._resc_version
                my_dict['roleRef'] = res1[0]['roleref']
                my_dict['subjects'] = [test1_dict]
            else:
                test_dict['name'] = resc_name
                test_dict['namespace'] = resc_namespace
                test1_dict['kind'] = 'ServiceAccount'
                test1_dict['apiGroup'] = ""
                test1_dict['namespace'] = resc_namespace
                test1_dict['name'] = test1[0]['name']
                my_dict['metadata'] = test_dict
                my_dict['kind'] = self._resc_kind
                my_dict['apiVersion'] = self._resc_version
                my_dict['roleRef'] = res[0]['roleref']
                my_dict['subjects'] = [test1_dict]
                my_dict['subjects'].extend(res[0]['subjects']) 
        elif resc_kind == 'clusterrole':
            test_dict['name'] = yaml_dict['name']
            my_dict['metadata'] = test_dict
            my_dict['kind'] = self._resc_kind
            my_dict['apiVersion'] = self._resc_version
            my_dict['rules'] = yaml_dict['rules']
        elif resc_kind == 'clusterrolebinding':
            test_dict['name'] = yaml_dict['name']
            my_dict['metadata'] = test_dict
            my_dict['kind'] = self._resc_kind
            my_dict['apiVersion'] = self._resc_version
            my_dict['subjects'] = yaml_dict['subjects']
            my_dict['roleRef'] = yaml_dict['roleRef']
        elif resc_kind == 'serviceaccount':
            test_dict['name'] = resc_name
            test_dict['namespace'] = resc_namespace
            my_dict['metadata'] = test_dict
            my_dict['kind'] = self._resc_kind
            my_dict['apiVersion'] = self._resc_version
        elif resc_kind == 'role':
            test_dict['name'] = yaml_dict['name']
            test_dict['namespace'] = resc_namespace
            my_dict['metadata'] = test_dict
            my_dict['kind'] = self._resc_kind
            my_dict['apiVersion'] = self._resc_version
            my_dict['rules'] = yaml_dict['rules']
        elif resc_kind == 'secret':
            my_dict['metadata'] = yaml_dict['secrets']
            my_dict['kind'] = self._resc_kind
            my_dict['apiVersion'] = self._resc_version
            my_dict['type'] = 'kubernetes.io/service-account-token'
        resc_new_yaml = pprint_to_yaml(my_dict)
        resc_yaml = yaml.safe_load(resc_new_yaml)
        return resc_yaml
 
    def create_resc_obj(self, resc_name):
        ret1 = []
        resc_kind = self._lookup_helper.resolve_var('resc_kind', default=None)
        resc_name = self._lookup_helper.resolve_var('resc_name', default=None)
        resc_namespace = self._lookup_helper.resolve_var('resc_namespace', default=None)
        kctl_action = 'diff' if self._diff_mode else self._action
        if not self._skip_generate:
            if resc_namespace is None and resc_kind == 'storageclass':
                resc_kind = self._lookup_helper.resolve_var('resc_kind', default=None)
                ret1 = self._read_storageclass_config_file()
            elif self._sub_action == 'all' and resc_kind == 'namespace':
                ret1 = self._read_all_custom_namespace_create()
            else:
                if resc_namespace is None and resc_kind != 'namespace' and resc_kind != 'storageclass':
                    new_resc_name = resc_name.replace('-','_') + '_' + self._resc_short_name +'_' + 'cfg'
                elif resc_namespace is None and resc_kind == 'namespace':
                    new_resc_name = 'ns' + '_' + resc_name.replace('-','_')
                elif resc_namespace is not None and resc_kind == 'role':
                    new_resc_name = resc_name.replace('-','_') + '_' + self._resc_short_name +'_' + 'cfg'
                else:
                    new_resc_name = 'ns' + '_' + resc_namespace.replace('-','_')
                resc_yaml = self._read_config_file(new_resc_name)
                k8s_obj = K8SResourceDefintion(self._lookup_helper, resc_yaml, filter_keys=False)
                skip_save = self._lookup_helper.resolve_var('skip_save', False)
                if not skip_save:
                    k8s_obj.save()
                ret1.append(k8s_obj.result)
                self.f_v("k8s_obj:\n{}", k8s_obj)
                        
        if not self._skip_kctl:
            if (self._sub_action == 'builtin' and resc_kind == 'storageclass') or (self._sub_action == 'all' and resc_kind == 'storageclass'):
                ret1 = self._read_storageclass_config_file_path()
                subpath=[]
                for value in ret1:
                    subpath.append(value['resource']['path'])
                for tmp_path in subpath:
                    results = self.do_kctl_cmd_single_resc(self._action, tmp_path, resc_namespace, additional_cmd_args=self._cmd_args)
                    ret1.extend(results)
            elif self._sub_action == 'all' and resc_kind == 'namespace':
                ret1 = self._apply_all_custom_namespace_create()
                subpath=[]
                for value in ret1:
                    subpath.append(value['resource']['path'])
                for tmp_path in subpath:
                    results = self.do_kctl_cmd_single_resc(self._action, tmp_path, resc_namespace, additional_cmd_args=self._cmd_args)
                    ret1.extend(results)
            else:    
                #resc_name = self._lookup_helper.resolve_var('resc_name', default=None)
                tmp_path = K8SResourceDefintion._build_manifest_path(self, self._k8s_paths, self._k8s_resc_api_def, resc_name, self._resc_namespace, manifest_dir=None)
                ret1 = self.do_kctl_cmd_single_resc(self._action, tmp_path, resc_namespace, additional_cmd_args=self._cmd_args)
        
        return ret1

    # BEGIN: Abstract methods/property for TaskHandler

    def supported_actions(self):
        """abstract property implementation"""
        return ('apply', 'diff', 'info', 'write', 'replace', 'update')

    def execute_task(self):
        """Handle add_on or app tasks"""
        kctl_action = 'diff' if self._diff_mode else self._action
        super(ResourceTaskHandler, self).execute_task(kctl_action)

        ret = []
        if self._action in ('info', 'diff'):
            ret = self.do_kctl_cmd_name(self._action, self._k8s_resc_api_def, 
                                    self._resc_names, resc_namespace=self._resc_namespace,
                                    additional_cmd_args=self._cmd_args)
        elif self._action in ('write',):
            # retrieve the resource from server
            # For apply do NOT allow if the resource already exists in server
            for resc_name in self._resc_names:
                resc_yaml = self._check_resource(self._k8s_resc_api_def, resc_name, self._resc_namespace)
                if resc_yaml is None:
                    raise AnsibleAssertionError("resource [{}] kind: [{}] does not exist on server".format(resc_name, self._k8s_resc_api_def.kind))
                # remove/filter not needed keys
                resc_yaml.setdefault('metadata', {}).setdefault('labels', {"app.kubernetes.io/managed-by": "live-cluster"})
                k8s_obj = K8SResourceDefintion(self._lookup_helper, resc_yaml, filter_keys=True)
                skip_save = self._lookup_helper.resolve_var('skip_save', False)
                if not skip_save:
                    k8s_obj.save()
                ret.append(k8s_obj.result)
                self.f_v("k8s_obj:\n{}", k8s_obj)
        elif self._action in ('apply',):
            if self._sub_action == 'builtin' or self._sub_action == 'all':
                ret = self.create_resc_obj(None)
            else:
                for resc_name in self._resc_names:
                    resc_yaml = self._check_resource(self._k8s_resc_api_def, resc_name, self._resc_namespace)
                    if resc_yaml is not None:
                        raise AnsibleAssertionError("resource [{}] kind: [{}] already exist cannot use 'apply', only update or replace allowed".format(resc_name, self._k8s_resc_api_def.kind))               
                    else:
                        ret = self.create_resc_obj(resc_name)
        elif self._action in ('replace',):
            if self._sub_action == 'builtin' or self._sub_action == 'all':
                ret = self.create_resc_obj(None)
            else:
                for resc_name in self._resc_names:
                    resc_yaml = self._check_resource(self._k8s_resc_api_def, resc_name, self._resc_namespace)
                    if resc_yaml is not None:
                        ret = self.create_resc_obj(resc_name)       
                    else:  
                        raise AnsibleAssertionError("resource [{}] kind: [{}] resource not found, cannot replace the resource".format(resc_name, self._k8s_resc_api_def.kind))

        elif self._action in ('update',):
            if self._sub_action == 'builtin' or self._sub_action == 'all':
                ret = self.create_resc_obj(None)
            else:
                for resc_name in self._resc_names:
                    resc_yaml = self._check_resource(self._k8s_resc_api_def, resc_name, self._resc_namespace)
                    if resc_yaml is not None:
                        ret = self.create_resc_obj(resc_name)
                    else:
                        raise AnsibleAssertionError("resource [{}] kind: [{}] resource not found, cannot update the resource".format(resc_name, self._k8s_resc_api_def.kind))
        return ret

    # END: Abstract methods for TaskHandler
