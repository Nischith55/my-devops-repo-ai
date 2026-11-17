# -*- coding: utf-8 -*-
"""Filter plugin to help with k8s support operations"""

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common._collections_compat import Mapping, Sequence, MutableSequence
from ansible.module_utils.six import string_types
from ansible.utils.display import Display

from copy import deepcopy
from json import dumps

import os

__metaclass__ = type

display = Display()

# key for extra directory to add..
K_EXTRA_DIR = 'extra_dirs'

def _check_for_sequence(obj, name):
    '''Utility method to check for sequence'''
    if not isinstance(obj, MutableSequence):
        raise AnsibleFilterError("{0} must be a Sequence type. Got {1}".format(name, type(obj)))
    #

def _check_for_mapping(obj, name):
    '''Utility method to check for mapping'''
    if not isinstance(obj, Mapping):
        raise AnsibleFilterError("{0} must be a Mapping type. Got {1}. {2}".format(name, type(obj), obj))
    #

def _check_for_string(obj, name):
    '''Utility method to check for string'''
    if not isinstance(obj, string_types):
        raise AnsibleFilterError("{0} must be a string type. Got {1}".format(name, type(obj)))
    #

class K8SMixin(object):
    """A mixin for k8s objects to be used by filter. Provides defaul properties
    and implementation.
    
    NOTES:
    - __init__ initializes the template params encapsulated in _dict
    """
    key_copy_config = 'copy_config'
    
    def __init__(self, config, *args, **kwargs):
        """Only thing we do is initialize the dict"""
        _check_for_mapping(config, 'base config object')
        self._dict = {}
        self._dict['name'] = config['name']
        if 'namespace' in config:
            self._dict['namespace'] = config['namespace']
        if 'kind' in config:
            self._dict['kind'] = config['kind']
        copy_config = kwargs.get(K8SMixin.key_copy_config, None)
        if copy_config is not None and copy_config:
            for k, v in config.iteritems():
                if k not in self._dict:
                    self._dict[k] = deepcopy(v)
            
    
    @property
    def name(self):
        return self._dict['name']

    @property
    def unique(self):
        """A string that uniquely identfies the instance of this class"""
        return '_'.join((self.name, self._dict.get('namespace', ''), self._dict.get('kind', '')))

    @property
    def to_dict(self):
        """A dictionary object that can be passed to templates"""
        return deepcopy(self._dict)

    def __str__(self):
        return dumps(self.to_dict, indent=2)
      
    __repr__ = __str__

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

# class K8SMixin

class BindingsMixin(object):
    """Mixin for role or cluster role binding or role binding operations"""
    
    @staticmethod
    def create_binding_config(kind, namespaces, bindings_spec_list):
        _check_for_sequence(namespaces, 'namespace list')
        _check_for_sequence(bindings_spec_list, 'binding specification list')
       
        ns_binding_map = dict()
        for ns_obj in namespaces:
            if kind == RoleBinding.kind:
                ns_binding_config_list = ns_obj.role_binding_configs
            elif kind == ClusterRoleBinding.kind:
                ns_binding_config_list = ns_obj.cluster_role_binding_configs
            else:
                raise AnsibleFilterError("Unsupported kind : {0}".format(kind))
            #
            for ns_binding_config in ns_binding_config_list:
                b_name = ns_binding_config['name']
                # WARNING cluster_role_binding should NEVER have namespace
                b_namespace = ns_binding_config['namespace'] if kind == RoleBinding.kind else ''
                binding_key = '_'.join((b_name, b_namespace))
                if binding_key not in ns_binding_map:
                    ns_binding_map[binding_key] = ns_binding_config
                else:
                    b_subjects = ns_binding_config.get('subjects', [])
                    ns_binding_map[binding_key]['subjects'].extend(b_subjects)
        # for ns_obj
        # Note: we use deepcopy to make a copy of the spec
        binding_spec_map = dict(((b_spec['name'], deepcopy(b_spec)) for b_spec in bindings_spec_list))
        binding_list = []
        for b_config in ns_binding_map.values():
            name = b_config['name']
            if name not in binding_spec_map:
                raise AnsibleFilterError("Binding specification not found. {0} Please configure it".format(name))
            #
            b_spec = binding_spec_map[name]
            binding = deepcopy(b_config)
            for k, v in b_spec.iteritems():
                if k != 'subjects':
                    binding[k] = deepcopy(v)
                #
            #
            subjects = binding.get('subjects', [])
            # add spec subjects
            b_spec_subjects = b_spec.get('subjects', [])
            display.vvvv("kind: {0}, spec subjects: {1}, binding subjects: {2}"
                      .format(kind, dumps(b_spec_subjects, indent=2), dumps(subjects, indent=2)))
            subjects.extend(b_spec_subjects)
            binding['subjects'] = subjects
            # Only append to final list if there are subjects
            if len(subjects) > 0:
                binding_list.append(binding)
        #
        display.vvv("binding_list: {0}".format(dumps(binding_list, indent=2)))
        return binding_list
# class BindingsMixin

class ClusterRole(K8SMixin):
    """A Cluster role K8S object for filter operations
    
    NOTES:
    - The main purpose is to setup output directory paths
    """
    kind = 'cluster_role'
    key_config = kind + 's'
    dir_name = key_config.replace('_', '-')
    
    def __init__(self, config):
        super(ClusterRole, self).__init__(config, copy_config=True)
        # add extra dirs for deployment file
        self._dict[K_EXTRA_DIR] = os.path.join(ClusterRole.dir_name)
#

class StorageClasss(K8SMixin):
    """A storage class K8S object for filter operations
    
    NOTES:
    - The main purpose is to setup output directory paths
    """
    kind = 'storage_class'
    key_config = kind + 'es'
    dir_name = key_config.replace('_', '-')
    
    def __init__(self, config):
        super(StorageClasss, self).__init__(config, copy_config=True)
        # add extra dirs for deployment file
        self._dict[K_EXTRA_DIR] = os.path.join(StorageClasss.dir_name)
#

class PersistentVolume(K8SMixin):
    """A Persistent Volume K8S object for filter operations
    
    NOTES:
    - The main purpose is to setup output directory paths, even though it can
      have namespace we ignore
    """
    dir_name = 'persistent-volumes'
    
    def __init__(self, config):
        super(PersistentVolume, self).__init__(config, copy_config=True)
        # add extra dirs for deployment file
        self._dict[K_EXTRA_DIR] = os.path.join(PersistentVolume.dir_name)
#

          
class Secret(K8SMixin):
    """A generic Secret Object.
    
    NOTES:
    - implements various k8s secrets current Opaque and DockerConfigJson imple-
      mented.
    
    """
    # secret name key in namespace configuration
    key_secret_name = 'secret_name'
    # supported secret kinds
    kind_secrets = ('generic_secret', 'registry_secret', 'tls_secret')
    kind_key_secret_map = dict(((k, k + 's') for k in kind_secrets))
    key_secrets = kind_key_secret_map.values()
    # output dirname mapping replace '_' with '-'
    dir_name_map = dict(((k, k.replace('_', '-') + 's') for k in kind_secrets))
    # Class var lookup key for secret contents
    key_data = 'secret_data'
    key_data_encoded = 'secret_data_encoded'
    key_labels = 'labels'
    registry_xform = {
        'client-id' : 'username',
        'client-secret': 'password',
        'email' : 'email',
        'registries': 'registries',
    }
    registry_suffix = '-regcred'
    
    @classmethod
    def create_instance(cls, kind, config):
        """Constructor for a secret object"""
        _check_for_mapping(config, 'secret object')
        if 'namespace' not in config:
            raise AnsibleFilterError("All secrets must have a namespace key in config")
        namespace = config['namespace']
        if kind not in Secret.kind_secrets:
            raise AnsibleFilterError("no secret kind {0} supported".format(kind))
        _config = {}
        if kind in ('generic_secret', 'tls_secret'):
            _config['name'] = config['name']
            # get all pure string data
            uncoded_data = dict()
            for k, v in config.iteritems():
                if k in ('name', 'namespace', 'data_encoded', 'labels'):
                    continue
                #
                uncoded_data[k] = deepcopy(v)
            #
            _config[Secret.key_data] = uncoded_data
            # get all encoded data
            data_encoded = config.get('data_encoded', {})
            _check_for_mapping(data_encoded, 'data_encoded')
            encoded_data = dict()
            for k, v in data_encoded.iteritems():
                encoded_data[k] = deepcopy(v)
            _config[Secret.key_data_encoded] = encoded_data
            # get all labels
            data_labels = config.get('labels', {})
            _check_for_mapping(data_labels, 'data_labels')
            labels_data = dict()
            for k, v in data_labels.iteritems():
                labels_data[k] = deepcopy(v)
            _config[Secret.key_labels] = labels_data
        elif kind == 'registry_secret':
            # TODO: this will break since Secret should also have unique for type!!
            skip_suffix = config.get('skip_suffix', False)
            _config['name'] = config['name'] if skip_suffix else config['name'] + Secret.registry_suffix
            _config[Secret.key_data] = {}
            for attr,xform_attr in Secret.registry_xform.iteritems():
                _config[Secret.key_data][xform_attr] = config[attr]
            #
        #
        _config['namespace'] = namespace
        # add kind as a marker
        _config['kind'] = kind
        # add extra dirs for deployment file
        _config[K_EXTRA_DIR] = os.path.join('namespaces', namespace, Secret.dir_name_map[kind])
        return Secret(_config)
    #
    
    def __init__(self, config):
        super(Secret, self).__init__(config)
        if 'kind' not in config:
            raise AnsibleFilterError("Cannot create 'Secret' object directly please use factory 'create'")
        # copy all remaining k,v into _dict.
        for k, v in config.iteritems():
            if k not in self._dict:
                self._dict[k] = deepcopy(v)
        
    @property
    def namespace(self):
        return self._dict['namespace']
    
    @staticmethod
    def create_secrets(kind, secret_spec_list, ns_secrets_map):
        """Create all secrets give the configuration.
        
        NOTES:
        - secret_spec_list is an list of secret configuration (like SPN secrets)
        - ns_secrets_map: is all secrets configured in namespace file.
        """
        _check_for_mapping(ns_secrets_map, "namespace secrets")
        _check_for_sequence(secret_spec_list, "all secret specification")
        display.vvv("secret_spec_list: {0}".format(dumps(secret_spec_list, indent=2)))
        ret = []
        # note the key is what is in config (e.g. registry_secrets etc..)
        key_map = Secret.kind_key_secret_map[kind]
        ns_secret_config_list = ns_secrets_map.get(key_map, [])
        display.vvvv("create_secrets ({0}): ns_secret_config_list {1}".format(kind, dumps(ns_secret_config_list, indent=2)))
        secret_spec_map = dict(((s['name'], s) for s in secret_spec_list))
        for ns_secret_cfg in ns_secret_config_list:
            # check make sure secret exists in spec
            sec_name = ns_secret_cfg[Secret.key_secret_name]
            if sec_name not in secret_spec_map:
                raise AnsibleFilterError("Secret name {0} has no specfication, not configured?".format(sec_name))
            _config = dict(((k, deepcopy(v)) for k, v in ns_secret_cfg.iteritems() if k != Secret.key_secret_name))
            secret_spec = secret_spec_map[sec_name]
            for k, v in secret_spec.iteritems():
                _config[k] = deepcopy(v)
            sec_obj = Secret.create_instance(kind, _config)
            ret.append(sec_obj)
        #
        return ret
#: class


class Subject(K8SMixin):
    """A K8S subject object"""
    
    service_account = 'ServiceAccount'
    key_service_accounts = 'service_accounts'
    dir_name_service_accounts = key_service_accounts.replace('_', '-')
    
    def __init__(self, config):
        """Constructor for creating a subject doubles as creation of service accounts
        
        IMPORTANT:
          - For service accounts since we have a manifest make sure K_EXTRA_DIR is
            availble. use create_service_account_config
        """
        super(Subject, self).__init__(config)
        if 'alias' in config:
            self._dict['alias'] = config['alias']
        #
        if config['kind'] == Subject.service_account:
            # must have namespace
            self._dict['namespace'] = config['namespace']
            # also add extra_dir
            self._dict[K_EXTRA_DIR] = config[K_EXTRA_DIR]
    
    @staticmethod
    def create_service_account_config(name, namespace):
        """Create a service account config object. Useful for creating the subject"""
        ret = {}
        ret['name'] = name
        ret['namespace'] = namespace
        ret['kind'] = Subject.service_account
        # service accounts have their own templates
        ret[K_EXTRA_DIR] = os.path.join('namespaces', namespace, Subject.dir_name_service_accounts)
        return ret
        
# class Subject


class ClusterRoleBinding(BindingsMixin, K8SMixin):
    """A cluster binding Object. The purpose of this class is to create an
    instance of cluster role binding.
    
    NOTES:
    - First all cluster role bindings from namespaces are collected from config-
      uration. IMPORTANT only service accounts are eligible.
    
    """
    
    kind = 'cluster_role_binding'
    key_config = kind + 's'
    dir_name = key_config.replace('_', '-')

    def __init__(self, config):
        """Initialization for the object, please use classmethod factory"""
        #NOTE: we want to copy all config items!!
        super(ClusterRoleBinding, self).__init__(config, copy_config=True)
     
    @classmethod
    def create_instance(cls, config):
        """Factory for Cluster Role Binding"""
        _check_for_mapping(config, 'cluster role binding')
        _config = {}
        _config['name'] = config['name']
        _config['kind'] = config['kind']
        _config['role_kind'] = config['role_kind']
        # the role reference
        _config['role'] = config['role']
        # add extra dirs for deployment file
        _config[K_EXTRA_DIR] = os.path.join(ClusterRoleBinding.dir_name)
        # get the built-in subjects
        _subjects_from_config_list = config.get('subjects', [])
        # now subjects from namespaces (aka service accounts
        _subjects = set((Subject(subject_config) for subject_config in _subjects_from_config_list))
        _config['subjects'] = [subj_obj.to_dict for subj_obj in _subjects]
        return ClusterRoleBinding(_config)
    #

    @staticmethod
    def create_cluster_role_binding_config(name):
        """Create a blank cluster role binding config object"""
        ret = {}
        ret['name'] = name
        ret['subjects'] = []
        return ret
    #
# class ClusterRoleBinding

class RoleBinding(BindingsMixin, K8SMixin):
    """A Standard Role Binding Object"""
    
    kind = 'role_binding'
    key_config = kind + 's'
    dir_name = key_config.replace('_', '-')
    
    def __init__(self, config):
        super(RoleBinding, self).__init__(config)
        _check_for_mapping(config, 'role_binding config')
        self._dict = deepcopy(config)

    @classmethod
    def create_instance(cls, config):
        """Constructor for Role Binding"""
        _check_for_mapping(config, 'role binding')
        if 'namespace' not in config:
            raise AnsibleFilterError("role binding config requres a namespace")
        namespace = config['namespace']
        _config = {}
        _config['namespace'] = namespace
        _config['name'] = config['name']
        _config['kind'] = config['kind']
        _config['role_kind'] = config['role_kind']
        # the role reference
        _config['role'] = config['role']
        # get the built-in subjects
        _subjects_from_config_list = config.get('subjects', [])
        _subjects = set((Subject(subject_config) for subject_config in _subjects_from_config_list))
        _config['subjects'] = [subj_obj.to_dict for subj_obj in _subjects]

        #
        # add extra dirs for deployment file
        _config[K_EXTRA_DIR] = os.path.join('namespaces', namespace, RoleBinding.dir_name)
        return RoleBinding(_config)
    #
    
class Namespace(K8SMixin):
    """A namespace object"""
    
    def __init__(self, config):
        """initialize a namespace object using the config"""
        #NOTE: we want to copy all CONFIG
        super(Namespace, self).__init__(config, copy_config=True)
        self._dict['labels'] = config.get('labels', {})
        if len(self._dict['labels']) == 0:
            display.v("WARNING: namespace: {0}, has no 'labels' defined".format(self._dict['name']))
        # annotations
        self._dict['annotations'] = config.get('annotations', {})
        self._dict[K_EXTRA_DIR] = os.path.join('namespaces', config['name'])
        self._service_accounts = Namespace._parse_service_accounts(config)
        self._rb_configs = Namespace._parse_role_bindings(config)
        self._crb_configs = self._parse_cluster_role_bindings(config)
        self._secret_config_map = self._parse_secrets(config)
    #

    @property
    def cluster_role_binding_configs(self):
        """Return all cluster role binding configs"""
        return deepcopy(self._crb_configs)
    
    @property
    def role_binding_configs(self):
        """Return all role binding configs"""
        return deepcopy(self._rb_configs)

    @property
    def secret_configs(self):
        """Return a map of ALL secret kinds for this namespace in a map"""
        return self._secret_config_map
    
    @property
    def service_accounts(self):
        return self._service_accounts
    
    @staticmethod
    def _parse_secrets(namespace_config):
        """Parse all types of secrets from namespace configuration"""
        ret = {}
        namespace = namespace_config['name']
        for key_secret in Secret.key_secrets:
            ret[key_secret] = []
            ns_secret_list = namespace_config.get(key_secret, [])
            display.vv("namespace: [{}], key_secret: [{}], ns_secret_list: {}".format(namespace, key_secret, dumps(ns_secret_list, indent=2)))
            _check_for_sequence(ns_secret_list, "namespace secrets")
            for ns_secret in ns_secret_list:
                _check_for_mapping(ns_secret, key_secret)
                _config = deepcopy(ns_secret)
                # Add namespace
                _config['namespace'] = namespace
                ret[key_secret].append(_config)
            #
        #
        display.v("_parse_secrets: {0}".format(dumps(ret, indent=2)))
        return ret      
        
    @staticmethod
    def _parse_cluster_role_bindings(namespace_config):
        """Scan and build the config for all cluster role bindings"""
        ret = []
        namespace = namespace_config['name']
        #NOTE: only service accounts have cluster role bindings
        for ns_sa_config in namespace_config.get(Subject.key_service_accounts, []):
            display.vvvvv("ns_sa_config: {0}".format(dumps(ns_sa_config, indent=2)))
            sa_config = Subject.create_service_account_config(ns_sa_config['name'], namespace)
            display.vvvvv("sa_config: {0}".format(dumps(sa_config, indent=2)))
            for crb_config in ns_sa_config.get(ClusterRoleBinding.key_config, []):
                _check_for_mapping(crb_config, "service account cluster role bindings")
                _crb_config = ClusterRoleBinding.create_cluster_role_binding_config(crb_config['name'])
                _crb_config['subjects'] = [sa_config]
                ret.append(_crb_config)
            #
        #
        display.vvv("namespace: {0}, parsed cluster role bindings: {1}".format(namespace, dumps(ret, indent=2)))
        return ret

    @staticmethod
    def _parse_role_bindings(namespace_config):
        """Parse all role_bindings in the namespace configuration, including service accounts"""
        # check we have any namespace level role_bindings, if yes get the subjects
        ns_rb_list = namespace_config.get(RoleBinding.key_config, [])
        namespace = namespace_config['name']
        ret = []
        for ns_rb in ns_rb_list:
            _check_for_mapping(ns_rb, 'namespace role_bindings')
            _ns_rb_config = {}
            ns_rb_name = ns_rb['name']
            subject_config_list = ns_rb.get('subjects', [])
            if len(subject_config_list) == 0:
                continue
            #
            _ns_rb_config['name'] = ns_rb['name']
            _ns_rb_config['namespace'] = namespace
            _ns_rb_config['subjects'] = subject_config_list
            ret.append(_ns_rb_config)
        #
        for ns_sa_config in namespace_config.get(Subject.key_service_accounts, []):
            ns_rb_list = ns_sa_config.get(RoleBinding.key_config, [])
            for ns_rb in ns_rb_list:
                sa_config = Subject.create_service_account_config(ns_sa_config['name'], namespace)
                _ns_rb_config = {}
                _ns_rb_config['name'] =  ns_rb['name']
                _ns_rb_config['namespace'] = namespace
                _ns_rb_config['subjects'] = [sa_config]
                ret.append(_ns_rb_config)
            #
        #
        display.vvv("namespace: {0}, Parsed Role Bindings: {1}".format(namespace, dumps(ret, indent=2)))
        return ret

    @staticmethod
    def _parse_service_accounts(namespace_config):
        """Create all ServiceAccount Objects in this namespace"""
        ns_sa_list = namespace_config.get(Subject.key_service_accounts, [])
        namespace = namespace_config['name']
        ret = set()
        for ns_sa in ns_sa_list:
            _check_for_mapping(ns_sa, 'namespace service_accounts')
            sa_config = Subject.create_service_account_config(ns_sa['name'], namespace)
            ret.add(Subject(sa_config))
        #
        return ret
# class Namespace

    
def build_k8s(ns_obj_list, kind, kind_config_list=None):
    """Generic build object"""
    _check_for_sequence(ns_obj_list, "namespaces")
    _check_for_string(kind, 'kind')
    if kind_config_list is not None:
        _check_for_sequence(kind_config_list, 'kind config objects')
    namespaces = [Namespace(ns_obj) for ns_obj in ns_obj_list]
    ret = []
    if kind == 'namespace':
        ret.extend((ns.to_dict for ns in namespaces))
    elif kind == 'cluster_role':
        # we don't need namespace
        cr_list = [ClusterRole(config) for config in kind_config_list]
        ret.extend((cr_obj.to_dict for cr_obj in cr_list))
    elif kind == 'storage_class':
        # we don't need namespace
        sc_list = [StorageClasss(config) for config in kind_config_list]
        ret.extend((sc_obj.to_dict for sc_obj in sc_list))
    elif kind == 'pv':
        # we don't need namespace
        pv_list = [PersistentVolume(config) for config in kind_config_list]
        ret.extend((pv_obj.to_dict for pv_obj in pv_list))
    elif kind == 'role_binding':
        rb_spec_list = RoleBinding.create_binding_config(kind, namespaces, kind_config_list)
        rb_list = [RoleBinding.create_instance(rb_spec) for rb_spec in rb_spec_list]
        ret.extend((rb.to_dict for rb in rb_list))
    elif kind == 'cluster_role_binding':
        crb_spec_list = ClusterRoleBinding.create_binding_config(kind, namespaces, kind_config_list)
        crb_list = [ClusterRoleBinding.create_instance(crb_spec) for crb_spec in crb_spec_list]
        ret.extend((crb.to_dict for crb in crb_list))
    elif kind == 'service_account':
        for ns in namespaces:
            ret.extend((sa.to_dict for sa in ns.service_accounts))
    elif kind in Secret.kind_secrets:
        #collect all secrets
        for ns in namespaces:
            ns_secret_config_map = ns.secret_configs
            ns_secret_list = Secret.create_secrets(kind, kind_config_list, ns_secret_config_map)
            ret.extend((ns_secret.to_dict for ns_secret in ns_secret_list))
        display.v("ret: {0}".format(dumps(ret, indent=2)))
    #
    return ret      


def appd_ns_to_instrument(namespaces, ns_start="pep-eiap-", join_str="|"):
    """Namespaces to auto-instrument, in appd format"""
    _check_for_sequence(namespaces, "namespaces")
    ns_list = []
    for ns in namespaces:
       _check_for_mapping(ns, "namespace")
       name = ns['name']
       if name.startswith(ns_start):
           ns_list.append(name)
    
    return join_str.join(ns_list)

def extract_secret_token_name(items, sa_name):
    '''Extract first secret token name from a namespace service account list'''
    if not isinstance(items, MutableSequence):
        raise AnsibleFilterError("'items' requires a Sequence, got {0} instead.".format(type(items)))
    if not isinstance(sa_name, string_types):
        raise AnsibleFilterError("Invalid setting identifier, {0} is not a string, its a {1}".format(sa_name, type(sa_name)))
    
    ret = None
    for i in items:
        i_sa_name = i['metadata']['name']
        if i_sa_name == sa_name:
            ret = i['secrets'][0]['name']
            break
        #
    #
    if ret is None:
        raise AnsibleFilterError("Could not find secret token name for SA '{0}'".format(sa_name))
    return ret

def sanitize_kctl_out(kctl_out):
    """Sanitize kubectl yaml output"""
    _check_for_mapping(kctl_out, "kubectl output")
    items = kctl_out.get('items', [])
    _check_for_sequence(items, "items")
    # ##
    # - They keys are level 1 fields in the output.
    # - to delete the level 1 subkey, set the value to None
    # ##
    delete_fields = {
        'metadata': [
            ('annotations', 'kubectl.kubernetes.io/last-applied-configuration'),
            'creationTimestamp',
            'managedFields',
            'resourceVersion',
            'selfLink',
            'uid',
        ],
        'spec': None,
        'status': None,
    }
    ret = []
    for item in items:
        _check_for_mapping(item, "item")
        obj = deepcopy(item)
        for _k, sub_key_list in delete_fields.iteritems():
            if sub_key_list is None:
                # delete
                if _k in obj:
                    del obj[_k]
            else:
                # get the top_value
                top_value = obj.get(_k, {})
                _check_for_mapping(top_value, _k)
                # we have to delete subkeys
                for s_key in sub_key_list:
                    if isinstance(s_key, string_types):
                        if s_key in top_value:
                            del top_value[s_key]
                    elif isinstance(s_key, (tuple, list)):
                        v = top_value
                        for _nested_key in s_key[:-1]:
                            v = v.get(_nested_key, {})
                        #
                        # delete the last key
                        last = s_key[-1]
                        if last in v:
                            del v[last]
                        #
                        # delete top_value first key if empty
                        first = s_key[0]
                        first_value = top_value.get(first, None)
                        if first_value is not None and len(first_value) == 0:
                            del top_value[first]
                    #
                #
            #
        #
        ret.append(obj)
    # for item
    return ret                 
                    
class FilterModule(object):
    ''' Ansible os helper'''
    
    def filters(self):
        return {
            'appd_ns_to_instrument': appd_ns_to_instrument,
            'build_k8s': build_k8s,
            'extract_secret_token_name': extract_secret_token_name,
            'sanitize_kctl_out': sanitize_kctl_out,
        }
    #
#
