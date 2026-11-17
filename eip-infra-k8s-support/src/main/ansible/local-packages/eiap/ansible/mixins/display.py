# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import os
import sys

from ansible.module_utils.six import string_types
from ansible.utils.display import Display
from eiap.ansible.helpers import (pprint_to_yaml,)
from yaml.representer import RepresenterError

class DisplayMixin(object):
    """Display Mixin Class

    IMPORTANT:
    - This is a mixin, no __init__ method so as to not accidentally create state
    """

    _mdisplay = Display()

    def _get_caller(self, frame=2):
        """Get the caller --- Note: can be extremely slow"""
        # NOTE: do not rely on _getframe, we use it for performance reason
        _stack = getattr(sys, '_getframe', None)
        _caller = 'Caller-Unknown'
        if _stack is not None:
            # we need the second stack
            try:
                _frame = _stack(frame)
                _caller = '{}:{}:{}'.format(os.path.basename(_frame.f_code.co_filename),
                                        _frame.f_code.co_name,_frame.f_lineno)
            except Exception:
                # we intentionally pass -- do not want to fail the call
                self._mdisplay.warning("DisplayMixin: failed to figure out caller")
                pass 
        return _caller

    def _display_msg(self, fmt, *args, **kwargs):
        """Display the message"""
        caller = self._get_caller(frame=3)
        new_args = list()
        for a in args:
            if isinstance(a, (tuple, dict, list)):
                try:
                    new_args.append(pprint_to_yaml(a))
                except RepresenterError as e: # @UnusedVariable
                    new_args.append(a)
            else:
                new_args.append(a)
        msg = ('[' + caller + ']:\n' + fmt).format(*new_args)
        color = kwargs.pop('color', 'white')
        self._mdisplay.display(msg, color=color, **kwargs)

    def f_console(self, fmt, *args, **kwargs):
        """convert to formatted string"""
        kwargs['color'] = 'bright yellow'
        self._display_msg(fmt, *args, **kwargs)

    def f_warning(self, fmt, *args, **kwargs):
        """convert to formatted string"""
        kwargs['color'] = 'bright purple'
        self._display_msg(fmt, *args, **kwargs)

    def f_v(self, fmt, *args, **kwargs):
        """convert to formatted string"""
        if self._mdisplay.verbosity > 0:
            kwargs['color'] = 'bright cyan'
            self._display_msg(fmt, *args, **kwargs)

    def f_vv(self, fmt, *args, **kwargs):
        """convert to formatted string"""
        if self._mdisplay.verbosity > 1:
            kwargs['color'] = 'cyan'
            self._display_msg(fmt, *args, **kwargs)

    def f_vvv(self, fmt, *args, **kwargs):
        """convert to formatted string"""
        if self._mdisplay.verbosity > 2:
            self._display_msg(fmt, *args, **kwargs)

    def f_vvvv(self, fmt, *args, **kwargs):
        """convert to formatted string"""
        if self._mdisplay.verbosity > 3:
            self._display_msg(fmt, *args, **kwargs)

    def f_vvvvv(self, fmt, *args, **kwargs):
        """convert to formatted string"""
        if self._mdisplay.verbosity > 4:
            self._display_msg(fmt, *args, **kwargs)

    def console(self, msg, *args, **kwargs):
        """Print a message to the console"""
        self.warning("Deprecated, please use f_console version")
        self._do_display('display', msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Print a message to the console"""
        self._do_display('warning', msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Print a message to the console"""
        self._do_display('debug', msg, *args, **kwargs)

    def v(self, msg, *args, **kwargs):
        """Print a message to the console 'v'"""
        self.warning("Deprecated, please use f_v version")
        self._do_display('v', msg, *args, **kwargs)

    def vv(self, msg, *args, **kwargs):
        """Print a message to the console 'vv' """
        self.warning("Deprecated, please use f_vv version")
        self._do_display('vv', msg, *args, **kwargs)

    def vvv(self, msg, *args, **kwargs):
        """Print a message to the console 'vvv'"""
        self.warning("Deprecated, please use f_vvv version")
        self._do_display('vvv', msg, *args, **kwargs)

    def vvvv(self, msg, *args, **kwargs):
        """Print a message to the console verbosity: 4 """
        self.warning("Deprecated, please use f_vvvv version")
        self._do_display('vvvv', msg, *args, **kwargs)

    def vvvvv(self, msg, *args, **kwargs):
        """Print a message to the console verbosity: 5 """
        self.warning("Deprecated, please use f_vvvvv version")
        self._do_display('vvvvv', msg, *args, **kwargs)

    def _do_display(self, mname, msg, *args, **kwargs):
        """Handle display method calls"""
        # NOTE: do not rely on _getframe, we use it for performance reason
        _stack = getattr(sys, '_getframe', None)
        _caller = 'Caller-Unknown'
        if _stack is not None:
            # we need the second stack
            try:
                _frame = _stack(2)
                _caller = '{}:{}:{}'.format(os.path.basename(_frame.f_code.co_filename),
                                        _frame.f_code.co_name,_frame.f_lineno)
            except Exception:
                # we intentionally pass -- do not want to fail the call
                self._mdisplay.warning("DisplayMixin: failed to figure out caller")
                pass 

        _mthd = getattr(self._mdisplay, mname, None)
        if _mthd is None:
            self._mdisplay.warning("DisplayMixin Failed, could not find method [{}] on Display Object".format(mname))
            return
        if isinstance(msg, string_types):
            if len(args) > 0:
                _msg = msg.format(*args)
            else:
                _msg = msg
            _mthd('[{}]:\n{}'.format(_caller, _msg), **kwargs)
        else:
            _mthd('[{}]:\n{}'.format(_caller, msg), **kwargs)

