# -*- coding: utf-8 -*-
"""
LookupModule: Query Cluster k8s supported api resources and version, additionally
any other metadata information.
"""
from __future__ import (absolute_import, division, print_function)
import os
import sys


"""
# #############################################################################
# IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT 
# Hack Alert:
# - Ansible does NOT allow *any* plugins to important python libraries except
#   except for what is in ansible.* namespace.
# - To overcome this we will use sys.path.insert to import OUR or any 3rd party
#   libraries
# - IMPORTANT: we use relative path as per this file location
# #############################################################################
# BEGIN HACK -- Check the relative path, if the file is moved PLEASE change
#               accordingly the python-libs location
"""
sys.path.insert(0, 
    os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..",  "local-packages")))
"""
# END Hack alert
"""
import traceback

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

from datetime import timedelta

from eiap.ansible.mixins.display import DisplayMixin
from eiap.ansible.lookup import LookupHelper
from eiap.k8s.api import K8SApiManager
from eiap.utils import (check_for_sequence, check_for_string,)

from timeit import default_timer as timer

__metaclass__ = type

class LookupModule(LookupBase):

    def __init__(self, *args, **kwargs):
        super(LookupModule, self).__init__(*args, **kwargs)

    def run(self, terms, variables=None, **kwargs): # @UnusedVariable (kwargs)
        check_for_sequence(terms, 'terms')
        _d = DisplayMixin()
        # NOTE: plugin loader should call the run method with variables=available_variables
        if variables is None:
            raise AnsibleError('No variables available in lookup environment')
        # create the lookup helper
        lookup_helper = LookupHelper(self._templar, variables, self._loader)
        # Build the K8S Api Manager
        try:
            _d.f_console("Starting K8SApiManager build")
            start = timer()
            k8s_api_mgr = K8SApiManager(lookup_helper)
            end = timer()
            _d.f_console("K8SApiManager build (time taken): {}ms", timedelta(milliseconds=end-start).microseconds)
            _d.f_console("K8SApiManager:\n{}", k8s_api_mgr)
        except:
            traceback.print_exc()
        ret = []
        for term in terms:
            _d.f_console("term: {}", term)
            check_for_string(term, "term")
        return ret

