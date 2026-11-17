# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import abc
import six

from eiap.ansible.helpers import NoAliasAnsibleDumper
from eiap.utils import collections_abc

"""
IMPORTANT:
- This package level there should be NO ansible dependencies.
"""

@six.add_metaclass(abc.ABCMeta)
class MappingMixin(collections_abc.MutableMapping):
    """A MappingMixin with default implementation for abc.MutableMapping

    IMPORTANT:
    - This is a mixin, no __init__ method so as to not accidentally create state
    """

    @staticmethod
    def yaml_representer(dumper, data):
        return dumper.represent_mapping(u'tag:yaml.org,2002:map', data.yaml_data)

    @property
    def yaml_data(self):
        """We use this for adding a yaml representer"""
        return self.data

    @abc.abstractproperty
    def data(self):
        pass

    @abc.abstractproperty
    def repr(self):
        pass

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # BEGIN: abstractmethod implementation of MutableMapping
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __getitem__(self, key):
        """Override getitem"""
        return self.data[key]

    def __delitem__(self, key):
        del self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    # END: abstractmethods MutableMapping
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __repr__(self):
        return self.repr

    __str__ = __repr__

# ## Add it to our representer
NoAliasAnsibleDumper.add_representer(
    MappingMixin,
    MappingMixin.yaml_representer
)
