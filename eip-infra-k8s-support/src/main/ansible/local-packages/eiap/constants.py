# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)


class K8SConstants(object):
    """Constants used across the board.
    """

    "Standard EIAP delimiter and conversion from - to _"
    delim = '_'

    add_ons_dir_name = 'add-ons'
    apps_dir_name = 'apps'
    generator_settings_filename = 'generator-settings.yml'
    kustomize_conf_filename = 'kustomize.conf.yml'
    kustomize_conf_template = kustomize_conf_filename + '.j2'

    overlays_dirname = 'overlays'
    manifests_dirname = 'manifests'

    resc_abbrev = 'resc_abbrev'

    yaml_dump_options = {
        'explicit_start': True,
        'default_flow_style': False,
        'indent': 2,
    }

    "All supported resource abbreviations"
    ra_namespace = 'ns'

    '''resc api keys: kr'''
    kr_resources_subdir = 'resources_subdir'
    kr_api_def = 'api_def'
    kr_namespaced = 'namespaced'
    kr_cluster_config_varnames = 'cluster_config_varnames'
    kr_cluster_config_varname_patterns = 'cluster_config_varname_patterns'
    kr_namespace_config_paths = 'namespace_config_paths'
    kr_config_merge_strategy = 'config_merge_strategy'
    kr_resc_def_required_keys = 'resc_def_required_keys'

    k_manifest_dir_fmt = 'manifest_dir_fmt'

    # BEGIN: variables
    v_k8s_api_refresh_cache = 'refresh_cache' # whether to referesh api-resources cache
    v_k8s_api_additional_cfg = 'k8s_api_resources_cfg' # additional configuration for k8s resource kind

    v_k8s_resource_meta = 'k8s_resource_meta' # deprecated

    v_subjects = 'k8s_sup_subjects'
    v_role_ref = 'k8s_role_ref'
    v_k8s_template_default_path = 'k8s_template_default_path'
    v_template_path = 'template_path'
    v_reources_save_basedir = 'api_resources_default_basedir'

    v_skip_generate = 'skip_generate'

#    v_buildin_storageclass = '^pep_eiap.+_sto_class_built_in$'

    v_cluster_name = 'cluster_name'
    # kustomization base dir rooted at add-on or app
    v_kustomize_base_dir = 'kustomize_base_dir'
    # CLI override variable for locating kustomize_conf filename
    v_kustomize_conf = 'kustomize_conf'
    # END: variables

    KIND_ORDER = {
        "Namespace": 0,
        "CustomResourceDefinition": 3,
        "StorageClass": 5,
        "PersistentVolume": 6,
        "PersistentVolumeClaim": 7,
        "ServiceAccount": 15,
        "Role": 20,
        "ClusterRole": 25,
        "RoleBinding": 30,
        "ClusterRoleBinding": 35,
        "ConfigMap": 40,
        "Secret": 45,
        "Service": 50,
        "Deployment": 55,
        "StatefulSet": 60,
        "DaemonSet": 65,
        "CronJob": 70,
        "PodDisruptionBudget": 75,
    }
    # always after CRD
    default_order = 4

    "Ansible built-in variable names"
    va_inv_host = 'inventory_hostname'
    va_host_vars = 'hostvars'
    va_playbook_dir = 'playbook_dir'
    v_src_root_dir = 'src_root_dir'

    '''keys for resc_params'''
    k_template_path = v_template_path

    def __init__(self):
        super(K8SConstants, self).__init__()
