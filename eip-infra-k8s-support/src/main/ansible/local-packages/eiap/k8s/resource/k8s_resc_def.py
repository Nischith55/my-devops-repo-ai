# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import getpass
import os

from ansible.errors import AnsibleAssertionError
from ansible.module_utils.common._collections_compat import Sequence

from copy import deepcopy
from functools import total_ordering
from socket import gethostname

from eiap.ansible.helpers import pprint_to_yaml
from eiap.ansible.lookup import LookupHelper
from eiap.constants import K8SConstants
from eiap.utils import (check_for_mapping, check_instance,
    check_key,)

from ..api import K8SApiManager
from ..path_vars import K8SPaths
from .mixins import K8SResourceMixin
from eiap.deepmerge_mergers import merge_list_append

@total_ordering # We use this to sort a list of k8s objects so it is applied or delete in order
class K8SResourceDefintion(K8SResourceMixin):
    """Encapsulates a K8S Resource Definition for a K8S Object. NOTE: this 
    implements a mapping interface so we can iterate.
    """

    eiap_labels = {
#        "app.kubernetes.io/managed-by": "kustomize",
#        "app.kubernetes.io/created-by": "Ansible-{}-{}".format(gethostname(), getpass.getuser())
    }

    def __init__(self, lookup_helper, k8s_obj_raw, **kwargs):
        """Constructor: initialize a K8S resource object

        params:
        - lookup_helper:
        - k8s_obj_raw: raw resource definition.
        - kwargs: [type:object]
            manifest_dir: the directory where the resource manifest is stored.
        """
        super(K8SResourceDefintion, self).__init__()
        check_for_mapping(k8s_obj_raw, "k8s_obj_raw")
        check_instance(lookup_helper, LookupHelper, "K8SResourceDefintion")
        self._lookup_helper = lookup_helper
        # singleton safe
        k8s_api_mgr = K8SApiManager(lookup_helper)
        k8s_paths = K8SPaths(lookup_helper)
        
        # sometimes the raw object is from a live server, see if we need to 
        # remove some keys before populating
        filter_keys = kwargs.get('filter_keys', False)
        if filter_keys:
            self._filter_resource_data(k8s_obj_raw)

        # fully resolve it and short var, also pop manifest path if present
        self._data = resc_def = deepcopy(lookup_helper.resolve(k8s_obj_raw))
        self.f_vvvv("resc_def (k8s_obj_raw):\n{}", resc_def)
        check_key('kind', resc_def, "K8SResourceDefintion")
        api_def = k8s_api_mgr.get_resource_api(resc_def['kind'])
        #print("mahesh_api_def", api_def)
        # check pre-conditions
        self._check_resc_def(resc_def, api_def)

        _C = K8SConstants
        metadata = resc_def['metadata']
        self._name = metadata['name']
        self._kind = resc_def['kind']
        self._namespace = metadata['namespace'] if 'namespace' in metadata else ''
        self._api_version = resc_def['apiVersion']
        tmp_manifest_path = resc_def.pop('manifest_path', kwargs.get('manifest_path', None))
        if tmp_manifest_path is None:
            # see if the resource has manifest_dir
            manifest_dir = resc_def.pop('manifest_dir', kwargs.get('manifest_dir', None))
            tmp_manifest_path = self._build_manifest_path(k8s_paths, api_def, self._name, self._namespace, manifest_dir)
        # we need to separate out the 'Namespace' and 'Secrets'
        self._manifest_path = self._process_manifest_path(k8s_paths, api_def, self._namespace, tmp_manifest_path)
        self.f_vv("manifest_path: [{}]", self._manifest_path)
        self._unique = _C.delim.join(filter(None, (self._name, self._namespace, self._kind)))
        # Always update EIAP labels
        metadata['labels'] = merge_list_append.merge(deepcopy(self.eiap_labels), metadata.get('labels', {}))
        
        # sort order
        self._order = _C.KIND_ORDER.get(self._kind, _C.default_order)
        self._repr = "{}".format(pprint_to_yaml(self._data))
        # keep a list of the result (like changed)
        self._result = {
            'changed': False,
            'resource': {
                'name': self._name,
                'apiVersion': self._api_version,
                'kind': self._kind,
                'namespace': self._namespace,
                'path': self._manifest_path,
            }
        }

    def _filter_resource_data(self, resc_yaml):
        """Filter not needed keys from live server resource object if retrieved
        via get resource.
        
        TODO:
        - This is hard-coded for now. Make it configurable or even ignore.
        """
        check_for_mapping(resc_yaml, "resc_yaml")
        resc_metadata = resc_yaml.get('metadata', {})
        resc_metadata.pop('creationTimestamp')
        resc_metadata.pop('managedFields','')
        resc_metadata.pop('resourceVersion')
        resc_metadata.pop('uid')
        resc_metadata_annotations = resc_metadata.get('annotations', {})
        resc_metadata_annotations.pop('kubectl.kubernetes.io/last-applied-configuration')
        return resc_yaml

    def _check_resc_def(self, resc_def, api_def):
        """Sanity check the resource definition provided"""
        for _k in ('apiVersion', 'metadata'):
            if _k not in resc_def:
                raise AnsibleAssertionError("'{}' must exist in resc_def:\n{}".format(_k, pprint_to_yaml(resc_def)))
        metadata = resc_def['metadata']
        if 'name' not in metadata:
            raise AnsibleAssertionError("'name' must exist in 'metadata':\n{}".format(pprint_to_yaml(metadata)))
        kind = resc_def['kind']
        if kind != 'Namespace' and api_def.namespaced:
            if 'namespace' not in metadata:
                raise AnsibleAssertionError("resc_def for kind: [{}] requires 'namespace'. metadata:\n{}".format(self._kind, pprint_to_yaml(resc_def)))

    def _build_manifest_path(self, k8s_paths, api_def, resc_name, resc_namespace, manifest_dir):
        """build the default manifest path"""
        if resc_name is None:
            resc_filename = ''
        else:    
            resc_filename = resc_name + '-' + api_def.short_name + '.yml'
        if resc_namespace is None:
            resc_namespace = ''
        if manifest_dir is None:
            manifest_dir = os.path.join(k8s_paths.deploy_root_dir, api_def.resource_subdir, resc_namespace)
        if api_def.kind == 'Secret':
            manifest_dir = os.path.join(k8s_paths.deploy_root_dir, api_def.resource_subdir, resc_namespace)
        manifest_path = os.path.join(manifest_dir, resc_filename)
        return manifest_path

    def _process_manifest_path(self, k8s_paths, api_def, resc_namespace, manifest_path):
        """Change the manifest path for certain resource kinds like Namespace and secrets
        NOTES:
        - if this is part of pre-kustomize aka overlays (temporary) resources than we
        just don't do any adjustments.
        """
        _C = K8SConstants
        if '/' + _C.overlays_dirname + '/' in manifest_path:
            return manifest_path
            
        if api_def.kind == 'Namespace':
            manifest_dir = os.path.join(k8s_paths.deploy_root_dir, api_def.resource_subdir)
            manifest_path = os.path.join(manifest_dir, os.path.basename(manifest_path))
        elif api_def.kind == 'Secret':
            # TODO: assert resc_namespace is not empty string
            manifest_dir = os.path.join(k8s_paths.secret_manifest_root_dir, api_def.resource_subdir, resc_namespace)
            manifest_path = os.path.join(manifest_dir, os.path.basename(manifest_path))
        return manifest_path

    @property
    def manifest_path(self):
        """Override: K8SResourceMixin

        NOTES:
        - Full path for where this resouces is stored
        """
        if self._manifest_path is None:
            raise AnsibleAssertionError("manifest_path is not set")
        return self._manifest_path

    @property
    def name(self):
        return self._name

    @property
    def namespace(self):
        return self._namespace

    @property
    def kind(self):
        return self._kind

    @property
    def result(self):
        """override K8SResourceMixin"""
        return self._result

    @property
    def sort_order(self):
        return self._order

    @property
    def api_version(self):
        return self._api_version

    @property
    def resc_def(self):
        """override K8SResourceMixin"""
        return self._data

    @property
    def unique(self):
        """A string that uniquely identfies the instance of this class"""
        return self._unique

    # BEGIN: abstract methods or properties
    @property
    def data(self):
        # always return a copy
        return deepcopy(self._data)

    @property
    def repr(self):
        return self._repr
    # END: abstract method or properties

    # BEGIN: required implementations for total_ordering
    def __gt__(self, other):
        return self.sort_order > other.sort_order

    def __ge__(self, other):
        return self.sort_order >= other.sort_order

    def __lt__(self, other):
        return self.sort_order < other.sort_order

    def __le__(self, other):
        return self.sort_order <= other.sort_order
    # END: required implementations for total_ordering

    def __eq__(self, other):
        # use type to deal with inheritance
        if type(other) is type(self):
            return self.unique == other.unique
        elif isinstance(other, Sequence) and len(other) == 3:
            _unique = '_'.join(other)
            return self.unique == _unique
        #
        return False

    def __ne__(self, other):
        """Must defined for Python 2"""
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.unique)

