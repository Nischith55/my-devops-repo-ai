from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    name: storage_class -- generate storage_classes
    author: MRK
    version_added: "2.9"
    short_description: TODO
    description:
      - TODO
    options:
      _terms:
        description: TODO
        required: True
      keys_map:
        description: The keys in the section to lookup must be a mapping, with value either None or default value
        required: True
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

from ansible.errors import AnsibleError, AnsibleAssertionError
from ansible.module_utils.common._collections_compat import Mapping, MutableSequence, Sequence
from ansible.module_utils.six import string_types
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
from copy import deepcopy
from json import dumps


display = Display()

def _check_for_sequence(obj, name):
    '''Utility method to check for sequence'''
    if not isinstance(obj, MutableSequence):
        raise AnsibleAssertionError("{0} must be a Sequence type. Got {1}".format(name, type(obj)))
    #

def _check_for_mapping(obj, name):
    '''Utility method to check for mapping'''
    if not isinstance(obj, Mapping):
        raise AnsibleAssertionError("{0} must be a Mapping type. Got {1}. {2}".format(name, type(obj), obj))
    #

def _check_for_string(obj, name):
    '''Utility method to check for string'''
    if not isinstance(obj, string_types):
        raise AnsibleAssertionError("{0} must be a string type. Got {1}".format(name, type(obj)))
    #

class LookupModule(LookupBase):

    PROVISIONERS = {
        'disk': 'kubernetes.io/azure-disk',
        'file': 'kubernetes.io/azure-file',
    }
    
    # This is the template variable name
    TMPL_VARNAME = '__azure_storage_class_template__'
    
    TMPL_PARAMS_VARNAME = '__tmpl_params__'
    
    def run(self, terms, sc_params=None, **kwargs):
        _check_for_sequence(terms, 'terms')
        if sc_params is None:
            raise AnsibleAssertionError("template params 'sc_params' must be specified")
        _check_for_mapping(sc_params, 'sc_params')
        display.vvv("terms: {0}, sc_params: {1}".format(terms, dumps(sc_params, indent=2)))
        # See if the default template varname was overridden
        tmpl_var = kwargs.get('template_varname', LookupModule.TMPL_VARNAME)
        tmpl_params_varname = kwargs.get('template_params_varname', LookupModule.TMPL_PARAMS_VARNAME)
        # current vars
        vars_save = getattr(self._templar, '_available_variables', {})
        # template variable MUST be Global
        if tmpl_var not in vars_save:
            raise AnsibleAssertionError("template variable not defined. {0}".format(tmpl_var))
        # save the raw
        tmpl_raw = vars_save[tmpl_var]
        ret = []
        # Convenient shorthand
        sc_types = LookupModule.PROVISIONERS
        # TODO: make sure we have only 1 term
        for term in terms:
            # each term is action
            display.vvv("storage_class 'term': {0}".format(term))
            _check_for_string(term, 'term')
            for name, params in sc_params.iteritems():
                _tmpl_params = deepcopy(params)
                display.v("'storage_class' Configuring: {0}".format('name'))
                # always add name, which will be SC name
                _tmpl_params['name'] = name
                if 'provisioner' not in params:
                    sc_t = params.get('type', None)
                    if sc_t not in sc_types:
                        raise AnsibleAssertionError("storage class type {0} invalid, supproted values are [{1}]".format(sc_t, sc_types.keys()))
                    _tmpl_params['provisioner'] = sc_types[sc_t]
                vars = deepcopy(vars_save)
                vars[tmpl_params_varname] = _tmpl_params
                self._templar.available_variables = vars
                item = self._templar.template(tmpl_raw, fail_on_undefined=True)
                ret.append(item)
        # for term
        return ret
