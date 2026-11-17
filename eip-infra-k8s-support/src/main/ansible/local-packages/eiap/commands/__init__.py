# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from .base import BaseCmd
from .istioctl import IstioctlCmd
from .kustomize import KustomizeCmd
from .kubectl import KubectlCmd

SUPPORTED_COMMANDS = {
    'istioctl': IstioctlCmd,
    'kustomize': KustomizeCmd,
    'kubectl': KubectlCmd,
}

__all__ = [
    'BaseCmd',
] + list(SUPPORTED_COMMANDS.values())
