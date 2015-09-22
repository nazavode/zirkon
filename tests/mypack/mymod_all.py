# -*- coding: utf-8 -*-

__all__ = [
    'five',
    'sixteen',
]

from .common import six, ten

def five():
    return 5

def sixteen():
    return six() + ten()
