from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: ini_helper -- note modified ini lookup for eiap need
    author: MRK
    version_added: "2.9"
    short_description: read a section from a ini file
    description:
      - "The ini_helper lookup reads the contents of a file in INI format C(key1=value1).
        This plugin retrieves the value on the right side after the equal sign C('=') of a given section C([section])."
    options:
      _terms:
        description: The section name to lookup
        required: True
      keys_map:
        description: The keys in the section to lookup must be a mapping, with value either None or default value
        required: False
      file:
        description: Name of the file to load.
        default: ansible.ini
      re:
        default: False
        type: boolean
        description: Flag to indicate if the key supplied is a regexp.
      encoding:
        default: utf-8
        description:  Text encoding to use.
"""

EXAMPLES = """
- debug: msg="User in some-section is {{ lookup('ini_helper', 'some-section', keys=['k8s_username'], file='users.ini') }}"

"""

RETURN = """
_raw:
  description:
    - value(s) of the keys in the section as a map, with key as key and its value
  type: map
  key: str
  value: str
"""
import os
import re
from io import StringIO

from ansible.errors import AnsibleError, AnsibleAssertionError
from ansible.module_utils.six.moves import configparser
from ansible.module_utils._text import to_bytes, to_text
from ansible.module_utils.common._collections_compat import Mapping, MutableSequence, Sequence
from ansible.module_utils.six import string_types
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
from copy import deepcopy

display = Display()

DEF_FILE = os.path.abspath(os.path.expanduser(os.path.expandvars("~/.azure/credentials")))

def _parse_kwargs(**kwargs):
    """Parse Keyword Arguments"""
    params = dict()
    """Making keys_map optional"""
    keys_map = kwargs.get('keys_map', {})
    if not isinstance(keys_map, Mapping):
        raise AnsibleAssertionError("'keys_map' must be a Mapping. {0}, type: {1}".format(keys_map, type(keys_map)))
    display.vvv("keys_map: {0}".format(keys_map))
    params['keys_map'] = keys_map
    params['encoding'] = kwargs.get('encoding', 'utf-8')
    params['type'] = kwargs.get('type', 'ini')
    params['re'] = kwargs.get('re', False)
    params['file'] = kwargs.get('file', DEF_FILE)
    return params
    
class LookupModule(LookupBase):

    def get_value(self, key, section, dflt, is_regexp):
        # Retrieve all values from a section using a regexp
        if is_regexp:
            return [v for k, v in self.cp.items(section) if re.match(key, k)]
        value = None
        # Retrieve a single value
        try:
            value = self.cp.get(section, key)
        except configparser.NoOptionError:
            return dflt
        return value
    
    def run(self, terms, variables=None, **kwargs):
        
        # parse kwargs
        params = _parse_kwargs(**kwargs)
        
        self.cp = configparser.ConfigParser()
        
        ret = []
        for term in terms:
            # each term is a section
            display.v("'term': {0}".format(term))
            if not isinstance(term, string_types):
                raise AnsibleError('Invalid setting identifier, "%s" is not a string, its a %s' % (term, type(term)))
            
            params['section'] = term
            
            # Retrieve file path
            path = self.find_file_in_search_path(variables, 'files',
                                                 params['file'])

            # Create StringIO later used to parse ini
            config = StringIO()
            # Open file using encoding
            contents, show_data = self._loader._get_file_contents(path)
            contents = to_text(contents, errors='surrogate_or_strict',
                               encoding=params['encoding'])
            config.write(contents)
            config.seek(0, os.SEEK_SET)

            self.cp.readfp(config)
            # Retrieve the whole section
            section_as_dict = dict(self.cp.items(params['section']))
            if len(params['keys_map']) == 0:
                ret_map = deepcopy(section_as_dict)
            else:
                ret_map = {}
                keys = params['keys_map'].keys()
                for key in keys:
                    value = self.get_value(key, params['section'],
                                         params['keys_map'][key], params['re'])
                    if value is None:
                        raise AnsibleAssertionError("key {0} does not exist".format(key))
                    # stuff it in a map
                    ret_map[key] = value
                # for key
            ret.append(ret_map)
        # for term
        return ret
