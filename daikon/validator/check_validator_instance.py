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
config.validator.check_validator_instance
=========================================
Implementation of the CheckValidatorInstance class
"""

__author__ = "Simone Campagna"
__all__ = [
    'CheckValidatorInstance',
]

from .check_type import CheckType
from .error import TypeValidationError
from .validator import Validator


class CheckValidatorInstance(CheckType):
    """CheckValidatorInstance()
       Check if key/value is a Validator instance.
    """
    TYPE = Validator

    def convert(self, key_value):
        if not isinstance(key_value.value, Validator):
            try:
                key_value.value = Validator.unrepr(key_value.value)
            except Exception as err:
                raise TypeValidationError(key_value, "cannot create a validator from string {!r}: {}: {}".format(
                    key_value.value,
                    type(err).__name__,
                    err,
                ))
