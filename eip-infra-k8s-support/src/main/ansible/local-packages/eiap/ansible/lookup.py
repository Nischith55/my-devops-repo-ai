# -*- coding: utf-8 -*-
"""
Module containing mixins for all ansible plugin types.
"""
from __future__ import (absolute_import, division, print_function)

from ansible.config.manager import ensure_type
from ansible.errors import (AnsibleUndefinedVariable, AnsibleAssertionError
                            , AnsibleError, AnsibleFileNotFound,
    AnsibleLookupError)
from ansible.module_utils._text import to_native, to_text, to_bytes
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.module_utils.six import string_types
from ansible.template import Templar
from contextlib import contextmanager
from copy import deepcopy
import re

from eiap.ansible.mixins import DisplayMixin
from eiap.constants import K8SConstants
from eiap.utils import (check_for_string, check_for_mapping)


class Undefined(object):
    """Custom undefined default, marker object"""
    
    def __str__(self):
        return to_text("UNDEFINED")
    
    __repr__ = __str__

_undefined = Undefined()

class LookupHelper(DisplayMixin):
    """class for helping with custom lookup plugin implementations.
    
    """
    
    DEFAULT_NEWLINE_SEQUENCE = "\n"

    def __init__(self, templar, variables, loader=None):
        super(LookupHelper, self).__init__()
        _classes = (Templar,)
        if not isinstance(templar, _classes):
            msg = "'lookup' must be instance of {0}".format(_classes)
            raise AnsibleAssertionError(to_native(msg))
        # save the templar
        self._templar = templar
        self._loader = loader
        self._vars_save = deepcopy(variables)
        self._global_varnames = list(self._vars_save.keys())
        self._template = templar.template
        self._initialize()

    @property
    def global_varnames(self):
        """Get all global  variable names"""
        return self._global_varnames

    @property
    def loader(self):
        return self._loader

    @property
    def templar(self):
        return self._templar

    def get_varnames(self, pattern):
        """Get All variable names with the input pattern"""
        check_for_string(pattern, "varname pattern: ")
        try:
            name = re.compile(pattern)
        except Exception as e:
            raise AnsibleError('Unable to use "{}" as a search parameter: %s' % (pattern, to_native(e)))
        varnames = []
        for varname in self.global_varnames:
            if name.search(varname):
                varnames.append(varname)
        #
        self.f_vvv("{}", varnames)
        return varnames

    def check_var_exists(self, variable):
        """Check if the variable exists in the inventory hostname or global

        Important no recursive checks are done. which means variable must be string.
        """
        _C = K8SConstants
        _vars = self._vars_save
        _host_vars = _vars[_C.va_host_vars]
        check_for_string(variable, "check_var_exists: variable")
        if variable in  self.global_varnames:
            return True
        if variable in  _host_vars[_vars[_C.va_inv_host]]:
            return True
        return False

    def resolve(self, obj, extra_vars=None, convert_bare=False, fail_on_undefined=True, **kwargs):
        """Resolve arbitrary object, if the object has templated strings, will resolve
        them recursively.

        Args:
                obj (str|list|tuple|map): object to resolve templated strings
                convert_bare (bool): whether `obj` will be enclosed in '{{' and '}}'
                fail_on_undefined (bool): whether to raise an exception if any variables is undefined
        IMPORTANT:
            - the original object will be returned if the object contains no templatized
              strings.
            - fail_on_defined is meant for if the variable itself is complex and contains
              templated variables, then it will return an exception
        """
        if extra_vars is None:
            '''Just to be safe, do we really need to do this?'''
            self._templar.available_variables = deepcopy(self._vars_save)
        else:
            _vars = deepcopy(self._vars_save)
            _vars.update(extra_vars)
            self._templar.available_variables = _vars
        value = self._template(obj, convert_bare=convert_bare, 
                                       fail_on_undefined=fail_on_undefined, **kwargs)

        return value

    def resolve_var(self, variable, default=_undefined, fail_on_none_value=True, fail_on_undefined=True, **kwargs):
        """
        Resolve a string variable, checking it exists and returns default if it is not None

        Args:
                variable (str) : 'bare' variable [should be global variable]
                default (Undefined) :
                fail_on_none_value (bool) :
                fail_on_undefined (bool) :

        IMPORTANT:
            - do NOT wrap in '{{' and '}}'
            - fail_on_defined is meant for if the variable itself is complex and contains
              templated varaibles, then it will return an exception
        """
        check_for_string(variable, "check_var_exists: variable")
        if not self.check_var_exists(variable):
            if not isinstance(default, Undefined):
                return default
            raise AnsibleUndefinedVariable("Variable: [{}] is not defined and no default provided".format(variable))
        '''
        - we extract the value of the global variable and then run the value 
          through the templating engine.
        - we do this to support variable names that have a '.' as it has special
          meaning in jinja2 syntax
        '''
        variable_value = self.get_var_raw(variable)
        self.f_vvvvv("variable: [{}], variable_value: [{}]", variable, variable_value)
        '''IMPORTANT: we have convert_bare has false'''
        value = self._template(variable_value, convert_bare=False, 
                                       fail_on_undefined=fail_on_undefined, **kwargs)
        #
        if fail_on_none_value and value is None:
            raise AnsibleError("value for variable: [{}] was <null>".format(variable))
        return value

    def get_var_raw(self, varname, default=_undefined, fail_on_none_value=True):
        """Get the value of the variable. Note the variable must be string an
        exception will be raised if default is `None` and fail_on_none_default if `True`

        Args:
            varname (str):
            default (object): A default value to return.
        NOTES:
        - First looked up via global variable
        - second looked up in inventory_hostname
        """
        check_for_string(varname, "get_var_raw: varname")
        _C = K8SConstants
        _vars = self._vars_save
        _host_vars = _vars[_C.va_host_vars]
        try:
            value = self._vars_save[varname]
        except KeyError:
            try:
                value = _host_vars[_vars[_C.va_inv_host]][varname]
            except KeyError:
                if isinstance(default, Undefined):
                    raise AnsibleUndefinedVariable('No variable found with this name: [{0}]'.format(varname))
                return default
        # if value is None (can happen if accidentally variable exist and empty
        if value is None:
            if fail_on_none_value and isinstance(default, Undefined):
                raise AnsibleUndefinedVariable('variable: [{}] has no value defined (bad config?)'.format(varname))
            value = default
        return value

    def _initialize(self):
        """Do some basic checks"""
        _C = K8SConstants
        for _v in (_C.va_host_vars, _C.va_inv_host):
            if _v not in self._vars_save:
                raise AnsibleError("Could not initialize LookupHelper. var: [{}] not in environment".format(_v))

    @contextmanager
    def get_template_data(self, source):
        # Get vault decrypted tmp file
        try:
            tmp_source = self._loader.get_real_file(source)
        except AnsibleFileNotFound as e:
            raise AnsibleLookupError("could not find template=%s, %s" % (source, to_text(e)))
        b_tmp_source = to_bytes(tmp_source, errors='surrogate_or_strict')

        try:
            with open(b_tmp_source, 'rb') as f:
                try:
                    template_data = to_text(f.read(), errors='surrogate_or_strict')
                except UnicodeError:
                    raise AnsibleLookupError("Template source files must be utf-8 encoded")
            yield template_data
        except AnsibleLookupError:
            raise
        except Exception as e:
            raise AnsibleError("%s: %s" % (type(e).__name__, to_text(e)))
        finally:
            self._loader.cleanup_tmp_file(b_tmp_source)

    def load_template(self, template, template_vars=None):
        extra_vars = dict() if template_vars is None else deepcopy(template_vars)
        check_for_mapping(extra_vars, "template_vars")

        if isinstance(template, string_types):
            # treat this as raw_params
            template_path = template
            newline_sequence = self.DEFAULT_NEWLINE_SEQUENCE
            variable_start_string = None
            variable_end_string = None
            block_start_string = None
            block_end_string = None
            trim_blocks = True
            lstrip_blocks = False
        elif isinstance(template, dict):
            template_args = template
            template_path = template_args.get('path', None)
            if not template:
                raise AnsibleError("Please specify path for template.")

            # Options type validation strings
            for s_type in ('newline_sequence', 'variable_start_string', 'variable_end_string', 'block_start_string',
                           'block_end_string'):
                if s_type in template_args:
                    value = ensure_type(template_args[s_type], 'string')
                    if value is not None and not isinstance(value, string_types):
                        raise AnsibleError("[{}] is expected to be a string, but got [{}] instead".format(s_type, type(value)))
            try:
                trim_blocks = boolean(template_args.get('trim_blocks', True), strict=False)
                lstrip_blocks = boolean(template_args.get('lstrip_blocks', False), strict=False)
            except TypeError as e:
                raise AnsibleError(to_native(e))

            newline_sequence = template_args.get('newline_sequence', self.DEFAULT_NEWLINE_SEQUENCE)
            variable_start_string = template_args.get('variable_start_string', None)
            variable_end_string = template_args.get('variable_end_string', None)
            block_start_string = template_args.get('block_start_string', None)
            block_end_string = template_args.get('block_end_string', None)
        else:
            raise AnsibleError("Error while reading template file - "
                                    "a string or dict for template expected, but got [{}] instead".format(type(template)))

        # Option `lstrip_blocks' was added in Jinja2 version 2.7.
        if lstrip_blocks:
            try:
                import jinja2.defaults
            except ImportError:
                raise AnsibleError('Unable to import Jinja2 defaults for determining Jinja2 features.')

            try:
                jinja2.defaults.LSTRIP_BLOCKS
            except AttributeError:
                raise AnsibleError("Option `lstrip_blocks' is only available in Jinja2 versions >=2.7")

        wrong_sequences = ["\\n", "\\r", "\\r\\n"]
        allowed_sequences = ["\n", "\r", "\r\n"]

        # We need to convert unescaped sequences to proper escaped sequences for Jinja2
        if newline_sequence in wrong_sequences:
            newline_sequence = allowed_sequences[wrong_sequences.index(newline_sequence)]
        elif newline_sequence not in allowed_sequences:
            raise AnsibleError("newline_sequence needs to be one of: \n, \r or \r\n")

        # template the source data locally & get ready to transfer
        with self.get_template_data(template_path) as template_data:
            # add ansible 'template' vars
            old_vars = self._templar.available_variables

            self._templar.environment.newline_sequence = newline_sequence
            if block_start_string is not None:
                self._templar.environment.block_start_string = block_start_string
            if block_end_string is not None:
                self._templar.environment.block_end_string = block_end_string
            if variable_start_string is not None:
                self._templar.environment.variable_start_string = variable_start_string
            if variable_end_string is not None:
                self._templar.environment.variable_end_string = variable_end_string
            self._templar.environment.trim_blocks = trim_blocks
            self._templar.environment.lstrip_blocks = lstrip_blocks
            variables = deepcopy(self._vars_save)
            variables.update(extra_vars)
            self._templar.available_variables = variables
            resultant = self._templar.do_template(template_data, preserve_trailing_newlines=True, escape_backslashes=False)
            self._templar.available_variables = old_vars
            return resultant
