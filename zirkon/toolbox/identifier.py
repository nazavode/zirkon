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
toolbox.identifier
==================
"""

__author__ = "Simone Campagna"
__all__ = [
    'is_valid_identifier'
]

import re


def is_valid_identifier(string):
    """is_valid_identifier(string) -> True/False
       Checks if 'string' is a valid identifier.
    """
    re_valid_key = re.compile(r"^[a-zA-Z_]\w*$")
    if not isinstance(string, str):
        return False
    if not re_valid_key.match(string):
        return False
    return True
