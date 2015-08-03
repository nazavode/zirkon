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
config.validator.check_type
===========================
Implementation of the CheckType class
"""

__author__ = "Simone Campagna"
__all__ = [
    'CheckType',
]

from .check import Check
from .error import TypeValidationError


class CheckType(Check):
    """CheckType()
       Check if key/value has type 'TYPE' or 'SECONDARY_TYPES'.
       If isinstance(value, SECONDARY_TYPES) then value is converted to 'TYPE'.
    """
    TYPE = type(None)
    SECONDARY_TYPES = None

    def check(self, key_value):
        value = key_value.value
        if not isinstance(value, self.TYPE):
            if self.SECONDARY_TYPES and isinstance(value, self.SECONDARY_TYPES):
                key_value.value = self.TYPE(value)
            else:
                raise TypeValidationError(key_value, "invalid type {} - expected type is {}".format(
                    type(value).__name__,
                    self.TYPE.__name__,
                ))
