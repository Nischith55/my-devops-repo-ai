# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from .k8s_resc_def import K8SResourceDefintion
from .kustomize_resc_def import KustomizeResourceDefintion

__all__ = [
    'K8SResourceDefintion',
    'KustomizeResourceDefintion',
]
