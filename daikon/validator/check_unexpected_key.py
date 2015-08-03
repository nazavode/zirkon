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

"""\
config.validator.check_unexpected_key
=====================================
Implementation of the CheckUnexpectedKey class
"""

__author__ = "Simone Campagna"
__all__ = [
    'CheckRequired',
]

from .check import Check
from .error import UnexpectedKeyValidationError


class CheckUnexpectedKey(Check):
    """CheckRequired()
       Check if a required key/value is available (no default).
    """

    def check(self, key_value):
        raise UnexpectedKeyValidationError(key_value, "unexpected key {!r}".format(key_value.key))
