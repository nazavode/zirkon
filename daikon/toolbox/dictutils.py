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
toolbox.dictutils
=================
Utility function for dictionaries.
"""

__author__ = "Simone Campagna"

__author__ = "Simone Campagna"
__all__ = [
    'as_dict',
    'compare_dicts',
]

import collections


def as_dict(dct, *, depth=-1, dict_factory=dict):
    """as_dict(dct, *, depth=-1, dict_class=dict) -> dict object
    """
    stddct = dict_factory(dct)
    dcts = [stddct]
    while depth != 0 and dcts:
        next_dcts = []
        for dct in dcts:
            for key, value in dct.items():
                if isinstance(value, collections.Mapping):
                    dct_value = dict_factory(value)
                    dct[key] = dct_value
                    next_dcts.append(dct_value)
        dcts = next_dcts
        if depth > 0:
            depth -= 1
    return stddct

def compare_dicts(dct0, dct1):
    """compare_dicts(dct0, dct1) -> True/False
    """
    stddct0 = as_dict(dct0, depth=-1, dict_factory=dict)
    stddct1 = as_dict(dct1, depth=-1, dict_factory=dict)
    return stddct0 == stddct1


