# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import os
import yaml

from ansible.errors import AnsibleAssertionError
from copy import deepcopy

from eiap.ansible.helpers import (pprint_to_yaml, NoAliasAnsibleDumper,
                                  read_yaml, write_yaml)
from eiap.ansible.lookup import LookupHelper
from eiap.ansible.mixins.display import DisplayMixin
from eiap.commands import KubectlCmd
from eiap.constants import K8SConstants
from eiap.deepmerge_mergers import merge_list_append
from eiap.k8s.path_vars import K8SPaths
from eiap.mixins import MappingMixin
from eiap.utils import (check_for_mapping, check_instance, check_for_sequence,
                        check_key, partition, check_for_string, hyphenate)

class K8SApiManager(DisplayMixin, MappingMixin):
    """Class encapsulating K8S Api resources sourced from target cluster

    IMPORTANT:
    - This is an expensive operation, so we make it a singleton and cache it
    - NO __init__ method, do the initialization in __new__
    CACHE REFRESH:
    - Make sure to refresh the cache if the api-spec is modified.
    - refresh also if any new CRD's or cluster upgrade happens.
    """

    # singleton instance
    _instance = None

    def __new__(cls, lookup_helper):
        """create a instance of the API Manager"""
        if cls._instance is None:
            cls._instance  = instance = super(K8SApiManager, cls).__new__(cls)
            # call __init__ in case any BaseClasses need it.
            super(cls, instance).__init__()
            # call the initialization code
            instance._initialize(lookup_helper)
        return cls._instance

    @staticmethod
    def yaml_representer(dumper, data):
        return dumper.represent_sequence(u'tag:yaml.org,2002:seq', data.yaml_data)

    def _initialize(self, lookup_helper):
        """Initialize the instance created from __new__

        IMPORTANT:
        - we don't use deprecated cache. Implement if u need it.
        TODO:
        - subresource is not supported, if you need it please implement another cache for it.
        """
        check_instance(lookup_helper, LookupHelper, "K8SApiManager")
        self._lookup_helper = lookup_helper
        self._k8s_paths = K8SPaths(self._lookup_helper)
        self._kctl_cmd = KubectlCmd.create(lookup_helper, use_default_cmd=True)
        self._repr = None
        self._data = self._load_api_resources(lookup_helper)
        # partition on preferred and nonpreferred
        preferred, nonpreferred = partition(lambda x: x.preferred_version, self._data)
        self._kind_cache = dict()
        self._name_cache = dict()
        self._deprecated_kind_cache = dict()
        self._deprecated_name_cache = dict()
        for obj in preferred:
            if not obj.subresource:
                kind_lower = obj.kind.lower()
                self._kind_cache.setdefault(kind_lower, []).append(obj)
                name_lower = obj.name.lower()
                self._name_cache.setdefault(name_lower, []).append(obj)
                # short name cache if not same as kind_lower
                if kind_lower != obj.short_name:
                    self._name_cache.setdefault(obj.short_name, []).append(obj)
        # handle cases where there are no preferred versions for a resource kind
        for obj in nonpreferred:
            if not obj.subresource:
                kind_lower = obj.kind.lower()
                if kind_lower not in self._kind_cache:
                    # ok there is no preferred version
                    self._kind_cache.setdefault(kind_lower, []).append(obj)
                else:
                    # deperecated
                    self._deprecated_kind_cache.setdefault(kind_lower, []).append(obj)
                name_lower = obj.name.lower()
                if name_lower not in self._name_cache:
                    self._name_cache.setdefault(name_lower, []).append(obj)
                    # short name cache if not same as kind_lower
                    if kind_lower != obj.short_name:
                        self._name_cache.setdefault(obj.short_name, []).append(obj)
                else:
                    self._deprecated_name_cache.setdefault(name_lower, []).append(obj)
        #

        self.f_vvvv("kind_cache:\n{}", self._kind_cache)
        self.f_vvvv("name_cache objs:\n{}", self._name_cache)
        # string representation include both extra data and api_data
        self._repr = "{}".format(pprint_to_yaml(self._data))

    def _load_api_resources(self, lookup_helper):
        """Load the api-resources by querying the k8s cluster or via cachefile if
        it exists.
        """
        _C = K8SConstants
        # additional data from our spec. NOTE: we use raw since we need to
        # resolve it lazily
        api_resources_cfg = lookup_helper.get_var_raw(_C.v_k8s_api_additional_cfg)
        self.f_vv("api_resources_cfg:\n{}", api_resources_cfg)
        check_for_mapping(api_resources_cfg, 'api_resources_cfg')
        refresh_cache = lookup_helper.resolve_var(_C.v_k8s_api_refresh_cache, default=False)
        cachefile_path = os.path.join(self._k8s_paths.deploy_root_dir, 'api', 'api-resources.yml')
        if not refresh_cache and os.path.exists(cachefile_path):
            self.f_console("api-resources building from: [{}]", cachefile_path)
            api_resources = read_yaml(cachefile_path)
            # create the k8s api resource object
            data = [K8SApiResource(self._lookup_helper, data, api_resources_cfg) for data in api_resources['api-resources']]
        else:
            # note: this is an expensive operation
            self.f_console("No api-resources cache file found: [{}], please be patient as we build or rebuild", cachefile_path)
            data= list()
            data.extend(self._build_core_api_resources(api_resources_cfg))
            data.extend(self._build_api_resources(api_resources_cfg))
            # spool it down to disk
            api_resources = {
                'api-resources': [k8s_api_resc.api_data for k8s_api_resc in data],
            }
            write_yaml(cachefile_path, api_resources)
        return data

    def _build_core_api_resources(self, api_resources_cfg):
        """Build the core API supported resources, querying the target cluster"""
        api_resource_objs = list()
        # 1. Get the core API version (NOTE: still legacy)
        result = self._kctl_cmd.execute('get', '--raw=/api')
        core_api_versions = yaml.safe_load(result['output'])
        check_for_mapping(core_api_versions, "core_api_versions")
        self.f_vv("core_api_versions:\n{}", core_api_versions)
        core_api_group_versions = core_api_versions['versions']
        check_for_sequence(core_api_group_versions, "core_api_group_versions")
        core_api_groups = tuple(K8SApiGroup('core', vers) for vers in core_api_group_versions)
        self.f_vv("{}", core_api_groups)
        for api_group_obj in core_api_groups:
            cmd_arg = '--raw=/api/{}'.format(api_group_obj.version)
            result = self._kctl_cmd.execute('get', cmd_arg)
            api_resources = yaml.safe_load(result['output'])
            check_for_mapping(api_resources, "api_resources")
            check_for_sequence(api_resources['resources'], "api_resources['resources']")
            api_resource_objs.extend((K8SApiResource.create_from_group(self._lookup_helper, api_group_obj, data, api_resources_cfg) for data in api_resources['resources']))
        self.f_vvv("core api_resource_objs:\n{}", api_resource_objs)
        return api_resource_objs

    def _build_api_resources(self, api_resources_cfg):
        """Build all the non core API resources, querying the target cluster"""
        api_resource_objs = list()
        result = self._kctl_cmd.execute('get', '--raw=/apis')
        api_group_list = yaml.safe_load(result['output'])
        check_for_mapping(api_group_list, "api_group_list")
        api_groups = list()
        for group_data in api_group_list['groups']:
            api_groups.extend(K8SApiGroup.create_from_group_list(group_data))
        self.f_vv("api_groups:\n{}", api_groups)

        for api_group_obj in api_groups:
            cmd_arg = '--raw=/apis/{}/{}'.format(api_group_obj.name, api_group_obj.version)
            result = self._kctl_cmd.execute('get', cmd_arg)
            api_resources = yaml.safe_load(result['output'])
            check_for_mapping(api_resources, "api_resources")
            check_for_sequence(api_resources['resources'], "api_resources['resources']")
            api_resource_objs.extend((K8SApiResource.create_from_group(self._lookup_helper, api_group_obj, data, api_resources_cfg) for data in api_resources['resources']))
        self.f_vvv("api_resource_objs:\n{}", api_resource_objs)
        return api_resource_objs

    # -------------------------------------------------------------------------
    # BEGIN: Public methods and properties
    # -------------------------------------------------------------------------

    def get_resource_api_kind_or_name(self, kind_or_name):
        """Get the resource api definition by resource kind or name

        NOTES:
        - we support short names also.
        """
        try:
            result = self.get_resource_api_by_name(kind_or_name)
        except AnsibleAssertionError as e: #@UnusedVariable
            result = self.get_resource_api(kind_or_name)

        return result

    def get_resource_api(self, kind):
        """Get the :class:`K8SApiResource` object for the kind

        IMPORTANT:
        - returned API is not a subresource
        - if the same name has MULTIPLE api groups we return the first one.. WATCH out
        """
        check_for_string(kind, "kind")
        kind_lower = kind.lower()
        if kind_lower not in self._kind_cache:
            raise AnsibleAssertionError("No API definition for kind found: [{}]".format(kind))
        api_kinds = self._kind_cache[kind_lower]
        if len(api_kinds) > 1:
            self.f_warning("The API resource kind: [{}] has multiple api groups, currently we support returning the first one", kind)
        return api_kinds[0]

    def get_resource_api_by_name(self, name):
        """Get the :class:`K8SApiResource` object by name

        IMPORTANT:
        - returned API is not a subresource
        - if the same name has MULTIPLE api groups we return the first one.. WATCH out
        """
        check_for_string(name, "name")
        name_lower = name.lower()
        if name_lower not in self._name_cache:
            raise AnsibleAssertionError("No API definition for name found: [{}]".format(name))
        api_names = self._name_cache[name_lower]
        if len(api_names) > 1:
            self.f_warning("The API resource name: [{}] has multiple api groups, currently we support returning the first one", name)
        return api_names[0]

    # BEGIN: abstract methods or properties
    @property
    def data(self):
        # always return a copy
        return deepcopy(self._data)

    @property
    def repr(self):
        return self._repr
    # END: abstract method or properties

# ## Add it to our representer
NoAliasAnsibleDumper.add_representer(
    K8SApiManager,
    K8SApiManager.yaml_representer
)

class K8SApiResource(DisplayMixin, MappingMixin):
    """A standard definition of K8S Resource aka GVK

    NOTES:
    """

    @classmethod
    def create_from_group(cls, lookup_helper, k8s_api_group, api_data, api_resource_cfg):
        """create from k8s_api_group data"""
        check_instance(k8s_api_group, K8SApiGroup, 'K8SApiResource')
        check_for_mapping(api_data, "K8SApiResource: api_data")
        _data = deepcopy(api_data)
        name = _data['name']
        _data['subresource'] = True if "/" in name else False
        if 'group' not in _data:
            _data['group'] = k8s_api_group.name

        if 'version' not in _data:
            _data['version'] = k8s_api_group.version
        _data['preferred_version'] = k8s_api_group.preferred_version
        instance = cls(lookup_helper, _data, api_resource_cfg)
        return instance

    def __init__(self, lookup_helper, api_data, api_resource_cfg):
        """Constructor: initialize a K8S API Resource

        NOTES:
        - if called directly e.g. via reading from cache the 'api_data' must be
          hydrated with all the pre-conditions
        """
        super(K8SApiResource, self).__init__()
        check_key('name', api_data)
        check_key('kind', api_data)
        check_key('subresource', api_data)
        check_key('group', api_data)
        check_key('version', api_data)
        check_key('preferred_version', api_data)
        check_instance(lookup_helper, LookupHelper, "K8SApiManager")
        self._lookup_helper = lookup_helper
        self._api_data = api_data
        self._extra_data = self._build_extra_data(api_data, api_resource_cfg)
        self._data = merge_list_append.merge(deepcopy(self._api_data), self._extra_data)
        # string representation include both extra data and api_data
        self._repr = "{}".format(pprint_to_yaml(self._data))
        self._unique = "{}-{}-{}".format(self._data['name'], self._data['group'], self._data['version'])

    def _build_extra_data(self, api_data, api_resource_cfg):
        """construct subdir for where this resource manifest will be persisted.

        NOTE:
        - this can be manipulated in resource definition class.
        """
        extra_data = dict()
        resource_cfg = api_resource_cfg.get('resources', {}).get(api_data['name'], {})
        check_for_mapping(resource_cfg, "resource_cfg")
        # retrieve the manifest_root_dirname is overridden else read global default.
        # see resource api-spec
        manifest_root_dir = resource_cfg.get('manifest_root_dirname', api_resource_cfg.get('defaults', {}).get('manifest_root_dirname', ''))
        short_names_data = api_data.get('shortNames', [])
        check_for_sequence(short_names_data, 'short_names_data')
        extra_data['short_name'] = resource_cfg.get('short_name', api_data['kind'].lower()) if len(short_names_data) == 0 else short_names_data[0]
        # subdir name
        suffix = (api_data['name'].partition("/")[0]).partition(api_data['kind'].lower())[2]
        default_subdir = hyphenate(api_data['kind']) + suffix
        extra_data['resource_subdir'] = os.path.join(manifest_root_dir, resource_cfg.get('resource_subdir', default_subdir))
        return extra_data

    # BEGIN: abstract methods or properties
    @property
    def data(self):
        # always return a copy
        return deepcopy(self._data)

    @property
    def repr(self):
        return self._repr
    # END: abstract method or properties

    @property
    def api_data(self):
        """mainly to write down the api-resources data"""
        return self._api_data

    @property
    def short_name(self):
        """return the short_name for this resource if defined else empty string"""
        return self._extra_data['short_name']

    @property
    def resource_subdir(self):
        """return the default subdir where the manifest for this resource will be stored"""
        return self._lookup_helper.resolve(self._extra_data['resource_subdir'])

    @property
    def name(self):
        return self._data['name']

    @property
    def kind(self):
        return self._data['kind']

    @property
    def preferred_version(self):
        return self._data['preferred_version']

    @property
    def namespaced(self):
        return self._data['namespaced']

    @property
    def group(self):
        return self._data['group']

    @property
    def version(self):
        return self._data['version']

    @property
    def subresource(self):
        return self._data['subresource']

    @property
    def api_version(self):
        return "{}".format(self.version) if self.group == 'core' else "{}/{}".format(self.group, self.version)

    @property
    def unique(self):
        """A string that uniquely identfies the instance of this class"""
        return self._unique

    def __eq__(self, other):
        # use type to deal with inheritance
        if type(other) is type(self):
            return self.unique == other.unique
        #
        return False

    def __ne__(self, other):
        """Must defined for Python 2"""
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.unique)

# ## Add it to our representer
NoAliasAnsibleDumper.add_representer(
    K8SApiResource,
    K8SApiResource.yaml_representer
)

class K8SApiGroup(DisplayMixin):
    """Class encapsulating a k8s api group object
    """
    @staticmethod
    def yaml_representer(dumper, data):
        return dumper.represent_mapping(u'tag:yaml.org,2002:map', data.yaml_data)

    @classmethod
    def create_from_group_list(cls, group_data):
        """APIGroupList groups data can have multiple versions with same name"""
        check_for_mapping(group_data, 'group_data')
        name = group_data['name']
        versions = group_data['versions']
        #preferred version
        preferred_version = group_data['preferredVersion']
        ret = list()
        for vd in versions:
            _vers = vd['version']
            obj = K8SApiGroup(name, _vers, preferred_version['version'] == _vers)
            ret.append(obj)
        return ret

    def __init__(self, name, version, preferred_version=True):
        """Initialize K8S API supported group and versions

        """
        super(K8SApiGroup, self).__init__()
        self._name = name
        self._version = version
        self._preferred_version = preferred_version
        self._data = {
            'apiGroup': {
                'name': self._name,
                'version': self._version,
            },
        }
        self._repr = None
        self._unique = "{}-{}".format(self._name, self._version)

    @property
    def yaml_data(self):
        return self._data

    @property
    def preferred_version(self):
        return self._preferred_version

    @property
    def is_core(self):
        return self._name == 'core'

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def api_version(self):
        return "{}".format(self.version) if self.name == 'core' else "{}/{}".format(self.name, self.version)

    @property
    def unique(self):
        """A string that uniquely identfies the instance of this class"""
        return self._unique

    def __eq__(self, other):
        # use type to deal with inheritance
        if type(other) is type(self):
            return self.unique == other.unique
        #
        return False

    def __ne__(self, other):
        """Must defined for Python 2"""
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.unique)

    def __repr__(self):
        if self._repr is None:
            self._repr = pprint_to_yaml(self._data)
        return self._repr

    __str__ = __repr__

# ## Add it to our representer
NoAliasAnsibleDumper.add_representer(
    K8SApiGroup,
    K8SApiGroup.yaml_representer
)
