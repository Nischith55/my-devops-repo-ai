# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import os
import yaml

from ansible.errors import (AnsibleAssertionError,)

from copy import deepcopy

from eiap.ansible.helpers import pprint_to_yaml
from eiap.ansible.lookup import LookupHelper
from eiap.commands import SUPPORTED_COMMANDS
from eiap.k8s.generators import KubectlGenerator
from eiap.utils import (check_for_mapping, check_for_sequence,
    check_for_string, check_instance, check_key,)

from .k8s_resc_def import K8SResourceDefintion
from .mixins import K8SResourceMixin
from ..settings import Settings

class KustomizeResourceDefintion(K8SResourceMixin):
    """Class encapsulating constructing a kustomization.yaml.
    """

    kustomize_filename = 'kustomization.yaml'

    def __init__(self, lookup_helper, settings):
        """Constructor: initialize a kustomization resource object.

        """
        super(KustomizeResourceDefintion, self).__init__()
        check_instance(settings, Settings, "KustomizeResourceDefintion")
        check_instance(lookup_helper, LookupHelper, "K8SResourceMixin")
        self._lookup_helper = lookup_helper
        self._repr = None
        self._settings = settings
        self._k8s_paths = settings.k8s_paths

        self._data = {
            'apiVersion': 'kustomize.config.k8s.io/v1beta1',
            'kind': 'Kustomization',
        }
        kustomize_data, kust_k8s_objs = self._build_kustomization_yaml(settings)
        self._data.update(kustomize_data)
        self._manifest_path = os.path.join(settings.overlays_dir, self.kustomize_filename)
        # update the result - note self is a k8s resource itself, we track all
        # resources that were generated as part of kustomize generation
        # keep a list of the result (like changed)
        self._result = dict()
        _kust_rescs_result = [k8s_obj.result for k8s_obj in kust_k8s_objs]
        self._result = {
            'kustomize': _kust_rescs_result,
        }

    def _handle_config_maps(self, settings):
        """Handle all config maps"""
        config_map_items = settings['kustomize_conf'].get('config_map_items', [])
        check_for_sequence(config_map_items, "config_map_items")
        config_map_generator = list()
        for item_raw in config_map_items:
            check_for_mapping(item_raw, "item_raw")
            item = self._lookup_helper.resolve(item_raw)
            check_key('name', item, add_msg="configMap item")
            cm_kust = {
                'name': item['name']
            }
            if 'options' in item:
                check_for_mapping(item['options'], "cm item options")
                cm_kust['options'] = item['options']
            # deal with files
            file_items = item.get('files', [])
            check_for_sequence(file_items, "file_items")
            files = list()
            for f in file_items:
                check_for_mapping(f, "file item")
                check_key('file', f, add_msg="file required")
                data_key = f.get('key', None)
                file_path = settings.resolve_path(f['file'])
                file_item = os.path.relpath(file_path, settings.overlays_dir)
                if data_key is not None:
                    file_item = "{}={}".format(data_key, file_item)
                files.append(file_item)
            if len(files) > 0:
                cm_kust['files'] = files
            #last
            config_map_generator.append(cm_kust)
        return config_map_generator

    def _handle_images(self, settings):
        """Handle kustomization images tag"""
        images = list()
        image_items = settings['kustomize_conf'].get('image_items', [])
        check_for_sequence(image_items, "image_items")
        for img_raw in image_items:
            check_for_mapping(img_raw, "image object")
            img = self._lookup_helper.resolve(img_raw)
            check_key('name', img, add_msg="image item")
            img_name = img['name']
            img_kust = {
                'name': img_name,
            }
            if 'newName' in img:
                img_kust['newName'] = img['newName']
            elif 'registry' in img:
                img_kust['newName'] = img['registry'] + '/' + img_name
            if 'newTag' in img:
                img_kust['newTag'] = img['newTag']
            # TODO: check and verify at least newTag or newName is in img_kust
            images.append(img_kust)
        return images

    def _build_dynamic_resources(self, external_commands):
        """These are resources generated dynamically using external commands.

        NOTES:
        - The k8s resources are valid k8s resources are mapping
        """
        check_for_sequence(external_commands, "external_commands")
        k8s_rescs = list()
        for cmd_data in external_commands:
            check_for_mapping(cmd_data, "cmd_data")
            check_key('name', cmd_data, add_msg='cmd_data')
            cmd_name = cmd_data['name']
            check_key(cmd_name, SUPPORTED_COMMANDS, add_msg="command not supported")
            use_default_cmd = cmd_data.get('use_default_cmd', False)
            cmd_obj = getattr(SUPPORTED_COMMANDS[cmd_name], 'create')(self._lookup_helper, use_default_cmd)
            check_key('method', cmd_data, add_msg='cmd_data')
            method = cmd_data['method']
            cmd_k8s_rescs = cmd_obj.dynamic_call(method, *cmd_data.get('args', []), **cmd_data.get('kwargs', {}))
            self.f_vvvv("k8s_rescs:\n{}", cmd_k8s_rescs)
            k8s_rescs.extend(cmd_k8s_rescs)
        return k8s_rescs

    def _build_kctl_generator_resources(self, kctl_generator_resources, default_namespace):
        """build the resources from kubectl command"""
        check_for_sequence(kctl_generator_resources, "kctl_generator")
        kctl_gen = KubectlGenerator(self._lookup_helper)
        k8s_rescs = list()
        for resc_cfg in kctl_generator_resources:
            check_for_mapping(resc_cfg, "resc_cfg")
            namespace = resc_cfg.get('namespace', default_namespace)
            k8s_resc = kctl_gen.generate(resc_cfg, namespace)
            k8s_rescs.append(k8s_resc)
        return k8s_rescs

    def _build_static_resources(self, settings, static_resources):
        """build the KRM resources list static

        Essentially, the objective is to convert path type resources to full
        path
        """
        check_for_sequence(static_resources, "static_resources")
        resources = list()
        for sr in static_resources:
            check_for_string(sr, "sr")
            resources.append(settings.resolve_path(sr))
        return resources

    def _handle_resources(self, settings):
        """Handle resources section of the KRM"""
        resources = list()
        default_namespace = settings['namespace']
        resources_from_cfg = settings['kustomize_conf'].get('resources', {})
        check_for_mapping(resources_from_cfg, "resources_from_cfg")

        # handle static resources
        static_resources_from_cfg = resources_from_cfg.get('static', [])
        static_resources = self._build_static_resources(settings, static_resources_from_cfg)
        resources.extend(static_resources)

        # handle generated resources
        kust_k8s_objs = list()
        generated_resources = resources_from_cfg.get('generated', {})
        check_for_mapping(generated_resources, "generated_resources")
        # 1) Do resources generated via external command
        generated_cmd_resources = generated_resources.get('external_commands', [])
        check_for_sequence(generated_cmd_resources, "generated_cmd_resources")
        # handle dynamic first.
        dynamic_k8s_rescs = self._build_dynamic_resources(generated_cmd_resources)
        dynamic_k8s_objs = [K8SResourceDefintion(self._lookup_helper, k8s_resc, manifest_dir=settings.overlays_dir) \
                                for k8s_resc in dynamic_k8s_rescs]
        # save the objects
        for k8s_obj in dynamic_k8s_objs:
            k8s_obj.save(generated='external_commands')
        kust_k8s_objs.extend(dynamic_k8s_objs)

        # 2) handle 'kctl_generator' resources
        kctl_generator_resources = generated_resources.get('kctl_generator', [])
        kctl_k8s_rescs = self._build_kctl_generator_resources(kctl_generator_resources, default_namespace)
        kctl_k8s_objs = [K8SResourceDefintion(self._lookup_helper, k8s_resc, manifest_dir=settings.overlays_dir) \
                                for k8s_resc in kctl_k8s_rescs]
        # save the objects
        for k8s_obj in kctl_k8s_objs:
            k8s_obj.save(generated='kctl_generator')
        kust_k8s_objs.extend(kctl_k8s_objs)
        # sort them
        kust_k8s_objs = sorted(kust_k8s_objs)
        resources.extend([k8s_obj.manifest_path for k8s_obj in kust_k8s_objs])
        # convert all to relative path
        resources = [os.path.relpath(rpath, settings.overlays_dir) for rpath in resources]
        return resources, kust_k8s_objs

    def _process_template_patch(self, settings, patch):
        """Handle template patch"""
        template_info = patch['template']
        template_path = settings.resolve_path(template_info)
        template_vars = {
            'template_params': patch['template_params'],
        }
        result = self._lookup_helper.load_template(template_path, template_vars)
        self.f_vvvv("template [{}] result:\n{}", template_path, result)
        ret = dict()
        if 'target' in patch:
            ret['target'] = patch['target']
        ret['patch'] = result
        return ret

    def _process_file_patch(self, name, patch_data):
        """Handle file patch"""
        _path = patch_data['file']
        _fullpath = self._k8s_paths.search_path_kustomize('files', name, _path)
        self.f_vv("Using file patch: [{}]", _fullpath)
        patch = dict()
        with open(_fullpath, "rb") as fd:
            _d = yaml.safe_load(fd)
            '''we will fully resolve it'''
            result = pprint_to_yaml(self._lookup_helper.resolve(_d))
        self.f_vvvv("file [{}] result:\n{}", _fullpath,result)
        patch['patch'] = result
        if 'target' in patch_data:
            patch['target'] = patch_data['target']
        return patch

    def _handle_patches(self, settings):
        """handle patches"""
        ret = list()
        patch_items = settings['kustomize_conf'].get('patch_items', [])
        check_for_sequence(patch_items, "patch_items")
        for patch in patch_items:
            check_for_mapping(patch, "patch object")
            if 'template' in patch:
                ret.append(self._process_template_patch(settings, patch))
            elif 'file' in patch:
                ret.append(self._process_file_patch(settings, patch))
            elif 'inline' in patch:
                patch_data = patch['inline']
                check_for_mapping(patch_data, "patch_data")
                inline_patch = {
                    'target': patch_data['target'],
                    # IMPORTANT: explicit_start to False, we don't want ---
                    'patch': pprint_to_yaml(patch_data['patch'], explicit_start=False)
                }
                ret.append(inline_patch)
            else:
                raise AnsibleAssertionError("'patch_items' should be list of objects with one of required keys ['file', 'template', 'inline']")

        self.f_vvvv("patches:\n{}", ret)
        return ret

    def _build_kustomization_yaml(self, settings):
        result = dict()
        result['namespace'] = settings['namespace']
        resources, kust_k8s_objs = self._handle_resources(settings)
        # we need only the resource paths for kust_k8s_objs
        result['resources'] = resources

        patches = self._handle_patches(settings)
        result['patches'] = patches
        result['images'] = self._handle_images(settings)
        result['configMapGenerator'] = self._handle_config_maps(settings)
        # global generator optiosn
        generator_options = settings['kustomize_conf'].get('generator_options', {})
        check_for_mapping(generator_options, "generator_options")
        result['generatorOptions'] = deepcopy(generator_options)
        return result, kust_k8s_objs

    # BEGIN: Abstract Properties
    @property
    def result(self):
        return self._result

    @property
    def data(self):
        return self._data

    @property
    def repr(self):
        if self._repr is None:
            self._repr = "{}".format(pprint_to_yaml(self.data))
        return self._repr

    @property
    def manifest_path(self):
        """Full path for where this resouces is stored"""
        return self._manifest_path

    @property
    def resc_def(self):
        """A valid K8S resource object, can be sent to API server
        """
        return self._data

    # END: Abstract Properties
