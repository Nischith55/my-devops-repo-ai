# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import abc
import os

from ansible.errors import AnsibleAssertionError

from eiap.ansible.mixins.display import DisplayMixin
from eiap.mixins import MappingMixin
from eiap.utils import (ensure_dir,)
from eiap.ansible.helpers import write_yaml

class K8SResourceMixin(DisplayMixin, MappingMixin):
    """A mixin for a k8s resource

    IMPORTANT:
    - This is a mixin, no __init__ method so as to not accidentally create state

    NOTES:
    - support reading from a file
    - reading a live k8s object
    - generating from a template
    - or plain raw object
    """

    def save(self, **kwargs):
        """Save the resource definition object"""
        dirname = os.path.dirname(self.manifest_path)
        if dirname != '' and dirname.startswith("/"):
            ensure_dir(dirname)
        else:
            raise AnsibleAssertionError("dirname [{}] for manifest_path, inconclusive: [{}]".format(dirname, self.manifest_path))
        write_yaml(self.manifest_path, self.resc_def)
        kwargs['changed'] = True
        self.update_result(**kwargs)

    def update_result(self, **kwargs):
        """update the result object"""
        # update the result with kwargs
        self.result.update(kwargs)
        #note some resource kind like Kustomization have no metadata
        name = self.resc_def.get('metadata', {}).get('name', os.path.basename(self.manifest_path))
        namespace = self.resc_def.get('metadata', {}).get('namespace', os.path.basename(self.manifest_path))
        self.result.update({
            'resource': {
                'name': name,
                'apiVersion': self.resc_def['apiVersion'],
                'kind': self.resc_def['kind'],
                'namespace': namespace,
                'path': self.manifest_path,
            }
        })

    @abc.abstractproperty
    def result(self):
        pass

    @abc.abstractproperty
    def resc_def(self):
        pass

    @abc.abstractproperty
    def manifest_path(self):
        pass

    def __getitem__(self, key):
        """Override getitem from MappingMixin"""
        return self.data[key]
