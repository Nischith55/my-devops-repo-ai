#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'core'}

DOCUMENTATION = r'''
---
module: k8s_deploy
short_description: Deploy k8s resources to the target cluster
description:
- TODO 1
- TODO 2
- TODO 3
version_added: '0.1.0'
options:
  msg:
    description:
    - The customized message that is printed. If omitted, prints a generic message.
    type: str
    default: 'Hello world!'
  var:
    description:
    - A variable name to debug.
    - Mutually exclusive with the C(msg) option.
    - Be aware that this option already runs in Jinja2 context and has an implicit C({{ }}) wrapping,
      so you should not be using Jinja2 delimiters unless you are looking for double interpolation.
    type: str
  verbosity:
    description:
    - A number that controls when the debug is run, if you set to 3 it will only run debug when -vvv or above
    type: int
    default: 0
    version_added: '2.1'
notes:
    - This module is also supported for Windows targets.
seealso:
- module: assert
- module: fail
author:
- EIAP Team
'''

EXAMPLES = r'''
# Example that prints the loopback address and gateway for each host
- debug:
    msg: System {{ inventory_hostname }} has uuid {{ ansible_product_uuid }}

- debug:
    msg: System {{ inventory_hostname }} has gateway {{ ansible_default_ipv4.gateway }}
  when: ansible_default_ipv4.gateway is defined

# Example that prints return information from the previous task
- shell: /usr/bin/uptime
  register: result

- debug:
    var: result
    verbosity: 2

- name: Display all variables/facts known for a host
  debug:
    var: hostvars[inventory_hostname]
    verbosity: 4

# Example that prints two lines of messages, but only if there is an environment value set
- debug:
    msg:
    - "Provisioning based on YOUR_KEY which is: {{ lookup('env', 'YOUR_KEY') }}"
    - "These servers were built using the password of '{{ password_used }}'. Please retain this for later use."
'''
