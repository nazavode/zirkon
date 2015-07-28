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
config.validator.check_validator
================================
Implementation of the CheckValidator class
"""

__author__ = "Simone Campagna"
__all__ = [
    'CheckValidator',
]

from .check_type import CheckType
from .error import TypeValidationError
from .validator import Validator


class CheckValidator(CheckType):
    TYPE = Validator
    def check(self, key_value):
        if key_value.defined:
            if isinstance(key_value.value, str):
                try:
                    validator = Validator.validator_unrepr(key_value.value)
                except Exception as err:
                    raise TypeValidationError(key_value, "cannot create a validator from string {!r}: {}: {}".format(
                        key_value.value,
                        type(err).__name__,
                        err,
                    ))
                key_value.value = validator
        return super().check(key_value)

