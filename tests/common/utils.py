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

__author__ = "Simone Campagna"
__all__ = [
    'to_standard_dict',
    'standard_dict',
    'compare_dicts',
]

import collections


def to_standard_dict(dct):
    if type(dct) != dict:
        return dict(dct)
    else:
        return dct

def standard_dict(dct):
    dct = to_standard_dict(dct)
    dcts = [dct]
    while dcts:
        next_dcts = []
        for dct in dcts:
            for key, value in dct.items():
                if isinstance(value, collections.Mapping):
                    dct_value = to_standard_dict(value)
                    dct[key] = dct_value
                    next_dcts.append(dct_value)
        dcts = next_dcts
    return dct
  
def compare_dicts(dct0, dct1):
    return standard_dict(dct0) == standard_dict(dct1)


