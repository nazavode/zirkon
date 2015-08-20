# -*- coding: utf-8 -*-
#
# Copyright 2013 Simone Campagna
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Utility function for dictionaries.
"""

__author__ = "Simone Campagna"

__author__ = "Simone Campagna"
__all__ = [
    'as_dict',
    'compare_dicts',
]

import collections


def as_dict(dct, *, depth=-1, dict_class=dict):
    """Returns a dict with the same content of the dct mapping.

       Parameters
       ----------
       dct: Mapping
           a dict-like object (dict, OrderedDict, Section, ...)
       depth: int, optional
           the depth of the copy (< 0 means full copy)
       dict_class: type, optional
           the dict class to be used for the copy

       Returns
       -------
       dict_class
           the converted dict
    """
    stddct = dict_class(dct)
    dcts = [stddct]
    while depth != 0 and dcts:
        next_dcts = []
        for dct in dcts:
            for key, value in dct.items():
                if isinstance(value, collections.Mapping):
                    dct_value = dict_class(value)
                    dct[key] = dct_value
                    next_dcts.append(dct_value)
        dcts = next_dcts
        if depth > 0:
            depth -= 1
    return stddct


def compare_dicts(dct0, dct1):
    """Compare two dictionaries. Converts the two dictionaries to standard dicts
       before. Used to avoid differences due to key ordering.

       Parameters
       ----------
       dct0: Mapping
           a dict-like object (dict, OrderedDict, Section, ...)
       dct1: Mapping
           a dict-like object (dict, OrderedDict, Section, ...)

       Returns
       -------
       bool
           True if the two dicts have the same content
    """
    stddct0 = as_dict(dct0, depth=-1, dict_class=dict)
    stddct1 = as_dict(dct1, depth=-1, dict_class=dict)
    return stddct0 == stddct1


def transform(dct, *, key_transform=None, value_transform=None, dict_class=None):
    """Transforms a dict by applying functions to keys and values.

       Parameters
       ----------
       dct: Mapping
           a dict-like object (dict, OrderedDict, Section, ...)
       key_transform: callable, optional
           a function to transform keys
       value_transform: callable, optional
           a function to transform values
       dict_class: type, optional
           the dict class to be used for the copy

       Returns
       -------
       dict_class
           the converted dict
    """

    if key_transform is None:
        key_transform = lambda key: key
    if value_transform is None:
        value_transform = lambda value: value
    if dict_class is None:
        use_dict_class = type(dct)
    else:
        use_dict_class = dict_class
    resdct = use_dict_class()
    for key, value in dct.items():
        key = key_transform(key)
        if isinstance(value, collections.Mapping):
            resdct[key] = transform(
                value,
                key_transform=key_transform,
                value_transform=value_transform,
                dict_class=dict_class)
        else:
            resdct[key] = value_transform(value)
    return resdct

