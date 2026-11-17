# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

'''
IMPORTANT:
- Absolutely NO Ansible dependent helpers should be here
'''
import collections
import errno
import os
import re
import pickle

'''
We need this to be compatible with Py3 and ansible six moves does not implement
this yet.
'''
try:
    # try Py3 first
    collections_abc = collections.abc # @UndefinedVariable
except AttributeError:
    collections_abc = collections # @UnresolvedImport

MutableMapping = collections_abc.MutableMapping
Mapping = collections_abc.Mapping
Sequence = collections_abc.Sequence
MutableSequence = collections_abc.MutableSequence

from json import dumps
from json.encoder import JSONEncoder
from six import string_types

class _PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, unicode, int, float, bool, type(None))):
            return JSONEncoder.default(self, obj)
        # check if we have a string implementation
        if type(obj).__str__ is not object.__str__:
            return {obj.__class__.__name__: obj.__str__()} 
        return {obj.__class__.__name__: pickle.dumps(obj)}
 
def to_nice_json_str(obj, indent=2, sort_keys=True):
    """Convert to nice json string"""
    return dumps(obj, indent=indent, cls=_PythonObjectEncoder, sort_keys=sort_keys)

def check_for_sequence(obj, name):
    '''Utility method to check for sequence'''
    '''Always eliminate string_types'''
    if isinstance(obj, string_types):
        raise AssertionError("{0} must be a Sequence type. Got {1}".format(name, type(obj)))
    if not isinstance(obj, (Sequence, MutableSequence)):
        raise AssertionError("{0} must be a Sequence type. Got {1}".format(name, type(obj)))
    #

def check_for_mapping(obj, name):
    '''Utility method to check for mapping'''
    if not isinstance(obj, (Mapping, MutableMapping)):
        raise AssertionError("{0} must be a Mapping type. Got {1}. {2}".format(name, type(obj), obj))
    #

def check_for_string(obj, name):
    '''Utility method to check for string'''
    if not isinstance(obj, string_types):
        raise AssertionError("{0} must be a string type. Got {1}".format(name, type(obj)))
    #

def check_key(key, _map, add_msg=''):
    """Check for key exist in map"""
    if key not in _map:
        raise AssertionError("no key: [{0}] found in map [{1}]. {2}".format(key, dumps(_map, indent=2), add_msg))

def check_instance(obj, class_or_type_or_tuple, pre_msg='instance'):
    """Check if obj is instance of the class or tuple of classes"""
    if not isinstance(obj, class_or_type_or_tuple):
        if not isinstance(class_or_type_or_tuple, Sequence):
            _cn = class_or_type_or_tuple.__name__
        else:
            _cn = ",".join(_c.__name__ for _c in class_or_type_or_tuple)
        raise AssertionError("[{}] must be instance of [{}]", pre_msg, _cn)

def ensure_dir(path, mode=0o755):
    """ensure a directory exists note: python 2.7 cannot avoid race condition"""
    check_for_string(path, "path")
    try:
        os.makedirs(path, mode)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def partition(pred, iterable):
    """
    Split the values into two sets, based on the return value of the function
    (True/False). e.g.:

        >>> partition(lambda x: x > 3, range(5))
        [0, 1, 2, 3], [4]
    """
    trues = []
    falses = []
    for item in iterable:
        if pred(item):
            trues.append(item)
        else:
            falses.append(item)
    return trues, falses

# BEGIN: Adapted from
# https://raw.githubusercontent.com/jpvanhal/inflection/master/inflection/__init__.py
def camelize(string, uppercase_first_letter= True):
    """
    Convert strings to CamelCase.

    Examples::

        >>> camelize("device_type")
        'DeviceType'
        >>> camelize("device_type", False)
        'deviceType'

    :func:`camelize` can be thought of as a inverse of :func:`underscore`,
    although there are some cases where that does not hold::

        >>> camelize(underscore("IOError"))
        'IoError'

    :param uppercase_first_letter: if set to `True` :func:`camelize` converts
        strings to UpperCamelCase. If set to `False` :func:`camelize` produces
        lowerCamelCase. Defaults to `True`.
    """
    if uppercase_first_letter:
        return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), string)
    else:
        return string[0].lower() + camelize(string)[1:]

def underscore(word, replace_hyphen=True):
    """
    Make an underscored, lowercase form from the expression in the string.

    Example::

        >>> underscore("DeviceType")
        'device_type'

    """
    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\1_\2', word)
    word = re.sub(r"([a-z\d])([A-Z])",r'\1_\2', word)
    if replace_hyphen:
        word = word.replace("-", "_")
    return word.lower()

def hyphenate(word, replace_underscore=True):
    """
    Make an dash, lowercase form from the expression in the string.

    Example::

        >>> hyphenate("DeviceType")
        'device_type'

    """
    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\1_\2', word)
    word = re.sub(r"([a-z\d])([A-Z])",r'\1_\2', word)
    if replace_underscore:
        word = word.replace("_", "-")
    return word.lower()



