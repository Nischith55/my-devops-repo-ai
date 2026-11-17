# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import os
import yaml

from ansible.errors import AnsibleError
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.module_utils._text import to_text
from ansible.parsing.yaml.dumper import AnsibleDumper
from eiap.constants import K8SConstants
from copy import deepcopy
from eiap.utils import ensure_dir

class NoAliasAnsibleDumper(AnsibleDumper):
    """Override Dumper to support dumping with no alias"""

    def ignore_aliases(self, data): # @UnusedVariable
        return True

def pprint_to_yaml(value, **kwargs):
    """Convert a value primarily a dictionary to nice yaml string"""

    ignore_aliases = boolean(kwargs.pop('no_aliases', True))
    explicit_start = boolean(kwargs.pop('explicit_start', True))
    indent = kwargs.pop('indent', 2)
    dumper = NoAliasAnsibleDumper if ignore_aliases else AnsibleDumper
    transformed = yaml.dump(value, Dumper=dumper, indent=indent, 
                            allow_unicode=True, default_flow_style=False, explicit_start=explicit_start, **kwargs)
    return to_text(transformed)

def read_yaml(path, **kwargs): # @UnusedVariable
    """Load a single object from the yaml file."""
    try:
        with open(path, "rb") as ifd:
            result = dict(yaml.safe_load(ifd))
    except Exception as e:
        raise AnsibleError("could not load file: [{}]. Error: [{}]".format(path, e.message))

    return result

def read_yaml_all(path, **kwargs): # @UnusedVariable
    """Write a single value to yaml file
    """
    try:
        with open(path, "rb") as ifd:
            result = list(yaml.safe_load_all(ifd))
    except Exception as e:
        raise AnsibleError("could not load file: [{}]. Error: [{}]".format(path, e.message))

    return result

def write_yaml(path, value, remove_file_on_error=True, allow_unicode=True, **kwargs):
    """Write a single value to yaml file"""
    write_yaml_all(path, [value], remove_file_on_error=remove_file_on_error, allow_unicode=allow_unicode, **kwargs)

def write_yaml_all(path, data, remove_file_on_error=True, allow_unicode=True, **kwargs):
    """Write a list of objects to yaml file"""
    _kwargs = deepcopy(K8SConstants.yaml_dump_options)
    _kwargs.update(kwargs)
    dirname = os.path.dirname(path)
    ensure_dir(dirname)
    try:
        with open(path, "w") as ofd:
            yaml.dump_all(data, ofd, Dumper=NoAliasAnsibleDumper, allow_unicode=allow_unicode, **_kwargs)
    except Exception as e:
        if remove_file_on_error:
            os.remove(path)
        raise AnsibleError("could not write to file: [{}]. Error: [{}]".format(path, e.message))
