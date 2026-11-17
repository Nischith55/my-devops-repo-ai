# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import os
import yaml

from ansible.errors import (AnsibleAssertionError,)

from copy import deepcopy

from eiap.ansible.helpers import pprint_to_yaml, NoAliasAnsibleDumper
from eiap.ansible.lookup import LookupHelper
from eiap.ansible.mixins.display import DisplayMixin
from eiap.constants import K8SConstants
from eiap.deepmerge_mergers import (merge_list_append, )
from eiap.k8s.path_vars import K8SPaths
from eiap.mixins import MappingMixin
from eiap.utils import (check_instance, check_for_string,
    check_key, check_for_sequence, check_for_mapping,
    ensure_dir,)

from six import iteritems

class Settings(DisplayMixin, MappingMixin):
    """An encapsulation of settings for an app or component instance

    parameters:
        lookup_helper: Our anisble variable resolver
        data_raw: [type: object] Raw data can contain jinja2 templates.
            extra_vars: [type: object] extra_vars in data_raw that will be used
                        to resolve the jinja2 variables.
    """

    def __init__(self, lookup_helper, k8s_paths, data_raw, app_name, component_name, is_add_on, src_kustomize_base_dir):
        super(Settings, self).__init__()
        check_instance(lookup_helper, LookupHelper, "Settings")
        _C = K8SConstants
        self._lookup_helper = lookup_helper
        self._data = dict()
        self._repr = None
        self._k8s_paths = k8s_paths
        # must exist
        check_key('name', data_raw, add_msg="'data_raw")
        # NOTE: name here is the instance name
        self._name = self._lookup_helper.resolve(data_raw['name'])
        # IMPORTANT: All data is recursively resolved.
        data_raw_copy = deepcopy(data_raw)
        extra_vars = data_raw_copy.pop('extra_vars', {})
        data_raw_resolved = self._lookup_helper.resolve(data_raw_copy, extra_vars=extra_vars)
        # update or mappingmixin dictionary
        self._data.update(data_raw_resolved)
        # TODO: both of these are already in AppSettings
        self._src_base_dir = os.path.join(self._k8s_paths.add_ons_base_dir if is_add_on \
                                                  else self._k8s_paths.apps_base_dir, app_name)
        self._data['src_base_dir'] = self._src_base_dir
        # generator directory
        self._data['src_kustomize_base_dir'] = src_kustomize_base_dir
        # We force a namespace
        check_key('namespace', data_raw, "Settings init")
        self._data['namespace'] = namespace = lookup_helper.resolve(data_raw['namespace'])
        deploy_additional_paths = filter(None, (component_name, namespace, self._name))
        # deploy_root_dir => deployments/<dept>/<env>/<cluster_name>/[add_ons|apps]
        self._deploy_base_dir = os.path.join(self._k8s_paths.deploy_root_dir, 
                                                       _C.add_ons_dir_name if is_add_on else _C.apps_dir_name, app_name,
                                                       *deploy_additional_paths)
        self._data['deploy_base_dir'] = self._deploy_base_dir
        self._deploy_manifests_dir = os.path.join(self._deploy_base_dir, _C.manifests_dirname)
        self._data['deploy_manifests_dir'] = self._deploy_manifests_dir
        ensure_dir(self._deploy_manifests_dir)
        self._overlays_base_dir = os.path.join(self._k8s_paths.overlays_root_dir,
                                                       _C.add_ons_dir_name if is_add_on else _C.apps_dir_name, app_name,
                                                       *deploy_additional_paths)

        self._deploy_overlays_dir = os.path.join(self._overlays_base_dir, _C.overlays_dirname)
        self._data['deploy_overlays_dir'] = self._deploy_overlays_dir
        ensure_dir(self._deploy_overlays_dir)

        manifest_filename = "-".join(filter(None, (app_name, component_name, self._name))) + '.yml'
        self._data['manifest_filename'] = manifest_filename
        self._data['manifest_path'] = os.path.join(self._deploy_manifests_dir, manifest_filename)

    def resolve_path(self, partial):
        """calculate the fullpath based on partial string"""
        check_for_string(partial, "partial")
        if partial.startswith("/"):
            return partial
        token, delim, remain = partial.partition(':')
        if remain.startswith("/"):
            return remain
        # if delim empty just parse remain, as it has to relative to genreator
        if delim == '':
            return os.path.join(self._data['src_kustomize_base_dir'], partial)
        if token == 'kustomize_root':
            return os.path.join(self._k8s_paths.global_kustomize_base_dir, remain)
        elif token == 'certs_root':
            return os.path.join(self._k8s_paths.certs_root_dir, remain)
        raise AnsibleAssertionError("Unsupported token: [{}]".format(token))

    @property
    def data(self):
        return self._data

    @property
    def repr(self):
        if self._repr is None:
            self._repr = "\n{}".format(pprint_to_yaml(self.data))
        return self._repr

    @property
    def k8s_paths(self):
        return self._k8s_paths

    @property
    def manifests_dir(self):
        return self._data['deploy_manifests_dir']

    @property
    def manifest_path(self):
        return self._data['manifest_path']

    @property
    def namespace(self):
        return self._data['namespace']

    @property
    def overlays_dir(self):
        return self._data['deploy_overlays_dir']

# ## Add it to our representer
NoAliasAnsibleDumper.add_representer(
    Settings,
    Settings.yaml_representer
)

class AppSettings(DisplayMixin, MappingMixin):
    """Holder class containing all the parameters neccessary to do generate the
    final manifests.
    """

    k_instances = 'instances'
    k_components = 'components'
    k_override_vars = 'override_vars'
    k_defaults = 'global_defaults'

    @classmethod
    def create_app_settings(cls, lookup_helper, is_add_on, app_name):
        k8s_paths = K8SPaths(lookup_helper)
        obj = cls(lookup_helper, k8s_paths, app_name, is_add_on, is_resc=False)
        return obj

    def __init__(self, lookup_helper, k8s_paths, name, is_add_on, is_resc):
        super(AppSettings, self).__init__()
        check_instance(lookup_helper, LookupHelper, "AppSettings")
        check_instance(k8s_paths, K8SPaths, "AppSettings")
        if is_add_on and is_resc:
            raise AnsibleAssertionError("is_add_on and is_resc cannot both be true")
        _C = K8SConstants
        self._lookup_helper = lookup_helper
        self._data = dict()
        self._repr = None
        self._k8s_paths = k8s_paths
        self._is_add_on = is_add_on
        self._data['name'] = self._data['app_name'] = self._name = self._app_name = name
        self._data['src_base_dir'] = os.path.join(self._k8s_paths.add_ons_base_dir if is_add_on \
                                                  else self._k8s_paths.apps_base_dir, name)
        # deploy_root_dir => deployments/<dept>/<env>/<cluster_name>/[add_ons|apps]
        self._data['deploy_base_dir'] = os.path.join(self._k8s_paths.deploy_root_dir, 
                                                       _C.add_ons_dir_name if is_add_on else _C.apps_dir_name, name)

        # generator directory
        self._data['src_kustomize_base_dir'] = os.path.join(self._data['src_base_dir'], 'kustomize')
        self._generator_settings_path = os.path.join(self._data['src_kustomize_base_dir'], _C.generator_settings_filename)
        app_settings = self.load_generator_settings(self._generator_settings_path)
        self._data.update(app_settings)
        self._app_components = tuple(app_settings.get('components', {}).keys())
        self._app_instances =  tuple(app_settings.get('instances', {}).keys())
        self._app_components_instances = dict([(k, tuple(v.get('instances', {}).keys())) for k, v in iteritems(app_settings.get('components', {}))])

    def _load_override_settings(self, varnames):
        """Load Override settings from a list of variable names"""
        check_for_sequence(varnames, "varnames")
        AS = AppSettings
        # IMPORTANT: override is raw which means the will be resolved upon
        # demand.
        override_settings = dict()
        for ovrd_v in varnames:
            val = self._lookup_helper.get_var_raw(ovrd_v, default={})
            check_for_mapping(val, "val")
            val_copy = deepcopy(val)
            if AS.k_override_vars in val:
                self.f_warning("Override variable [{}] has key: [{}] will be ignored", ovrd_v, AS.k_override_vars)
                del val_copy[AS.k_override_vars]
            merge_list_append.merge(override_settings, val_copy)
        #
        return override_settings

    def _load_instance_settings(self, instances, defaults):
        check_for_sequence(instances, "instances")
        check_for_mapping(defaults, "instance_global_defaults")
        instance_settings_all = dict()
        for inst in instances:
            check_for_mapping(inst, "instance")
            if 'name' not in inst:
                raise AnsibleAssertionError("'name' key missing in instance settings:\n{}".format(pprint_to_yaml(inst)))
            name = self._lookup_helper.resolve(inst['name'])
            if name in instance_settings_all:
                self.f_warning("Warning instance: [{}] already has previous configuration.", instance_settings_all[name])
                inst_settings = merge_list_append.merge(instance_settings_all[name], inst)
            else:
                inst_settings = merge_list_append.merge(deepcopy(defaults), inst)
            instance_settings_all[name] = inst_settings
        self.f_vvvvv("instance settings all:\n{}", instance_settings_all)
        return instance_settings_all

    def _load_component_settings(self, components, defaults):
        """Load all component settings for this app"""
        check_for_sequence(components, "components")
        check_for_mapping(defaults, "global_defaults")
        AS = AppSettings
        component_settings_all = dict()
        for comp in components:
            check_for_mapping(comp, "comp")
            if 'name' not in comp:
                raise AnsibleAssertionError("'name' key missing in comp:\n{}".format(pprint_to_yaml(comp)))
            component_name = self._lookup_helper.resolve(comp['name'])
            component_settings = dict()
            # merge with defaults (always override
            comp_defaults = comp.get(AS.k_defaults, {})
            check_for_mapping(comp_defaults, "comp_defaults")
            comp_defaults_merged = merge_list_append.merge(deepcopy(defaults), comp_defaults)
            comp_override_settings = self._load_override_settings(comp.get(AS.k_override_vars, []))
            # retrieve defaults from override
            comp_override_defaults = comp_override_settings.get(AS.k_defaults, {})
            check_for_mapping(comp_override_defaults, "comp_override_defaults")
            # Final merged component defaults
            merge_list_append.merge(comp_defaults_merged, comp_override_defaults)
            # Now settings for each instances of these components
            comp_instances_override = comp_override_settings.get(AS.k_instances, [])
            check_for_sequence(comp_instances_override, "comp_instances_override")
            comp_instances = comp.get(AS.k_instances, [])
            check_for_sequence(comp_instances, "comp_instances")
            # This has to be append, since we are setting default to []
            comp_instances_merged = merge_list_append.merge(deepcopy(comp_instances), comp_instances_override)
            # load all instances for this component
            component_settings[AS.k_instances] = self._load_instance_settings(comp_instances_merged, comp_defaults_merged)
            component_settings[AS.k_defaults] = comp_defaults_merged
            component_settings_all[component_name] = component_settings
        self.f_vvvvv("component_settings_all:\n{}", component_settings_all)
        return component_settings_all

    def load_generator_settings(self, generator_settings_path):
        self.f_v("generator_settings_path: [{}]", generator_settings_path)
        check_for_string(generator_settings_path, "generator_settings_path")

        with open(generator_settings_path, "rb") as ifd:
            gen_settings = yaml.safe_load(ifd)

        self.f_vv("gen_settings:\n{}", gen_settings)
        AS = AppSettings
        app_settings = dict()
        # global defaults for the app.
        app_global_defaults = gen_settings.get(AS.k_defaults, {})
        check_for_mapping(app_global_defaults, "app_global_defaults")
        app_instances = gen_settings.get(AS.k_instances, [])
        check_for_sequence(app_instances, "app_instances")

        app_override_vars = gen_settings.get(AS.k_override_vars, [])
        check_for_sequence(app_override_vars, "app_override_vars")
        app_override_settings = self._load_override_settings(app_override_vars)

        # merged global_defaults (app) level
        app_defaults_merged = merge_list_append.merge(deepcopy(app_global_defaults), 
                                                        app_override_settings.get(AS.k_defaults, {}))
        # Handle components first
        app_components = gen_settings.get(AS.k_components, [])
        check_for_sequence(app_components, "app_components")
        self.f_vvvv("app_components:\n{}", app_components)
        # This has to be append, since we are setting default to []
        components_merged = merge_list_append.merge(deepcopy(app_components), 
                                                       app_override_settings.get(AS.k_components, []))
        component_settings_all = self._load_component_settings(components_merged, app_defaults_merged)

        app_settings[AS.k_components] = component_settings_all

        # Handle instances
        app_instances = gen_settings.get(AS.k_instances, [])
        check_for_sequence(app_instances, "app_instances")
        # This has to be append, since we are setting default to []
        instances_merged = merge_list_append.merge(deepcopy(app_instances), 
                                                       app_override_settings.get(AS.k_instances, []))
        instances_settings_all = self._load_instance_settings(instances_merged, app_defaults_merged)
        app_settings[AS.k_instances] = instances_settings_all
        return app_settings

    def get_settings(self, instance_name, component_name=None):
        """Get the settings for the instance, with optional component name if the
        instance belongs to a component.
        """
        check_for_string(instance_name, "instance_name")
        AS = AppSettings

        # ##
        # TODO: Optimize the lookup resolve put it in a cache, if this is called
        # many times will be a performance hit
        # ##

        if instance_name not in self._app_instances and component_name is None:
            raise AnsibleAssertionError("could not locate settings for instance: [{}] for app: [{}]. Need Component?".format(instance_name, self._name))
        elif instance_name in self._app_instances:
            data_raw = self._data[AS.k_instances][instance_name]
            return Settings(self._lookup_helper, self._k8s_paths, data_raw, self._name, component_name, self._is_add_on, self._data['src_kustomize_base_dir'])
        elif component_name is not None:
            check_for_string(component_name, "component_name")
            if component_name in self._app_components_instances and instance_name in self._app_components_instances[component_name]:
                data_raw = self._data[AS.k_components][component_name][AS.k_instances][instance_name]
                return Settings(self._lookup_helper, self._k8s_paths, data_raw, self._name, component_name, self._is_add_on, self._data['src_kustomize_base_dir'])
            else:
                raise AnsibleAssertionError("Could not locate settings for instance: [{}] of component: [{}]".format(instance_name, component_name))

        else:
            raise AnsibleAssertionError("Could not locate settings for instance [{}] in app setings: [{}]".format(instance_name, self._name))
        #

    @property
    def data(self):
        return self._data

    @property
    def repr(self):
        if self._repr is None:
            self._repr = "\n{}".format(pprint_to_yaml(self.data))
        return self._repr

# ## Add it to our representer
NoAliasAnsibleDumper.add_representer(
    AppSettings,
    AppSettings.yaml_representer
)




