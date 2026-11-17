# -*- coding: utf-8 -*-
"""Filter plugin to help with istio support operations"""

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

def _get_enabled_gateways(gwy_cfg_list, gw_deploy_cfg_list):
    """we match Service IP and enabled flag"""
    ret = []
    for gwy_d in gw_deploy_cfg_list:
        if not gwy_d['enabled']:
            display.vv("Skipping {0}, disabled".format(gwy_d['name']))
            continue
        # match ip, we ALWAYS configure static ip
        ip_d = None
        controller_name = gwy_d['name']
        for overlay in gwy_d.get('k8s', {}).get('overlays', []):
            if overlay['kind'] == 'Service':
                for _p in overlay['patches']:
                    if _p['path'] == 'spec.loadBalancerIP':
                        ip_d = _p['value']
                if ip_d is None:
                    raise AnsibleFilterError("No static ip configured for service {0}".format(dumps(overlay, indent=2)))
                #
            #
        #
        # now match the ip with static config
        for gwy_cfg in gwy_cfg_list:
            if gwy_cfg['lb-ip'] == ip_d:
                _gwy_cfg = deepcopy(gwy_cfg)
                # add ingress or egress controller name controller name
                _gwy_cfg['controller_name'] = controller_name
                ret.append(_gwy_cfg)
                break
        #
    #
    return ret

def _build_gwy_template_params(gwy_cfg_list, cp_name, namespace):
    
    ret = []
    for gwy_cfg in gwy_cfg_list:
        istio_gw = {}
        # setup extra_dir - in the control-plane
        istio_gw[K_EXTRA_DIR] = os.path.join(namespace, cp_name, 'gateways')
        gw_name = istio_gw['name'] = gwy_cfg['name']
        istio_gw['namespace'] = namespace
        spec = istio_gw['spec'] = {}
        selector = istio_gw['spec']['selector'] = {}
        selector['istio'] = gwy_cfg['controller_name']
        servers = istio_gw['spec']['servers'] = []
        port_list = gwy_cfg['ports']
        default_hosts = gwy_cfg.get('hosts')
        for p in port_list:
            svr = {}
            port = svr['port'] = {}
            for k in ('name', 'number', 'protocol'):
                port[k] = p[k]
            svr['name'] = gw_name + '-' + port['protocol'] + '-' + str(port['number'])
            svr['hosts'] = default_hosts if (p.get('hosts', None) is None) else p['hosts']
            tls_settings = p.get('tls', None)
            if tls_settings is not None:
                svr['tls'] = deepcopy(tls_settings)
                # add secret_name only non http
                if port['protocol'].lower() not in ('http', ):
                    svr['tls']['credentialName'] = gwy_cfg['secret_name']
            #
            servers.append(svr)
        #
        ret.append(istio_gw)
        
    return ret

def get_istio_gateways(gwys_cfg, cp_deploy_cfg):
    """Get ENABLED gateway configuration by looking up the deployed control plane config
    
    TODO:
     - support egressGateways
    """
    _check_for_mapping(gwys_cfg, 'gwys_cfg')
    _check_for_mapping(cp_deploy_cfg, 'cp_deploy_cfg')
    display.v("gwys_cfg: {0}".format(dumps(gwys_cfg, indent=2)))
    ret = []
    # in from config
    in_gwy_cfg_list = gwys_cfg.get('in-gateways', [])
    in_gwy_d_list = cp_deploy_cfg.get('spec', {}).get('components', {}).get('ingressGateways', [])
    in_gwy_list = _get_enabled_gateways(in_gwy_cfg_list, in_gwy_d_list)
    cp_name = cp_deploy_cfg['metadata']['name']
    namespace = cp_deploy_cfg['metadata']['namespace']
    ret.extend(_build_gwy_template_params(in_gwy_list, cp_name, namespace))
    return ret

class FilterModule(object):
    ''' Ansible istio helper'''
    
    def filters(self):
        return {
            'get_istio_gateways': get_istio_gateways,
        }
    #
#
