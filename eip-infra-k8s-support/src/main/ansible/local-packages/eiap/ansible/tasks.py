# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from ansible.errors import AnsibleAssertionError, AnsibleError

from eiap.ansible.helpers import pprint_to_yaml, NoAliasAnsibleDumper
from eiap.ansible.mixins.display import DisplayMixin
from eiap.k8s.path_vars import K8SPaths
from eiap.utils import (check_instance, check_for_string, Mapping, Sequence, )

from .lookup import LookupHelper
from .task_handlers import TaskHandler
from eiap.k8s.api import K8SApiManager
from six import string_types

class TaskResult(DisplayMixin):
    """Basic Encapsulation of a single K8S Task"""

    @staticmethod
    def yaml_representer(dumper, obj):
        return dumper.represent_mapping(u'tag:yaml.org,2002:map', obj.data)

    def __init__(self, task_str):
        super(TaskResult, self).__init__()
        check_for_string(task_str, "task_str")
        self._data = dict()
        self._data['name'] = task_str
        self._data['results'] = list()

    def update_result(self, results):
        """update the result key"""
        if isinstance(results, (string_types, Mapping)):
            self._data['results'].append(results)
        elif isinstance(results, (Sequence,)):
            self._data['results'].extend(results)
        else:
            raise AnsibleAssertionError("update_result: accepts only string, mapping or sequence type. got [{}]".format(results))

    @property
    def name(self):
        return self._data['name']

    @property
    def changed(self):
        changed = False
        for _r in self._data['results']:
            changed = _r.get('changed', False)
            if changed: break
        return changed

    @property
    def skipped(self):
        skipped = False
        for _r in self._data['results']:
            skipped = _r.get('skipped', False)
            if skipped: break
        return skipped

    @property
    def data(self):
        return self._data

    def __repr__(self):
        return "{}".format(pprint_to_yaml(self._data))
    __str__ = __repr__

# ## Add it to our representer
NoAliasAnsibleDumper.add_representer(
    TaskResult,
    TaskResult.yaml_representer
)

class TaskManager(DisplayMixin):
    """Core K8S Task Manager - supporting multiple K8S Tasks"""

    @staticmethod
    def yaml_representer(dumper, obj):
        return dumper.represent_mapping(u'tag:yaml.org,2002:map', obj.data)

    def __init__(self, lookup_helper):
        super(TaskManager, self).__init__()
        check_instance(lookup_helper, LookupHelper, "TaskManager")
        self._lookup_helper = lookup_helper
        self._k8s_paths = K8SPaths(lookup_helper)
        self._k8s_api_mgr = K8SApiManager(lookup_helper)
        self._dict = dict()
        self._dict['k8s_paths'] = self._k8s_paths
        self._dict['k8s_api_mgr'] = self._k8s_api_mgr

        self.f_vvv("K8SApiManager:\n{}", self._k8s_api_mgr)

    def handle_task(self, task_str, **task_args):
        check_for_string(task_str, "task_str")
        task_result = TaskResult(task_str)
        task_handler = TaskHandler.create_from_task_str(self._lookup_helper, task_str, **task_args)
        if task_handler is None:
            raise AnsibleError("Could not determine task handler for: [{}]".format(task_str))

        results = task_handler.execute_task()
        task_result.update_result(results)
        self.f_v("task_result:\n{}", task_result)
        return task_result

    @property
    def data(self):
        return self._dict

    def __repr__(self):
        return "{}".format(pprint_to_yaml(self._dict))

    __str__ = __repr__

# ## Add it to our representer
NoAliasAnsibleDumper.add_representer(
    TaskManager,
    TaskManager.yaml_representer
)
