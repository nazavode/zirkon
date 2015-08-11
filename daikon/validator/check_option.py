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
config.validator.check_option
=============================
Implementation of the CheckOption class
"""

__author__ = "Simone Campagna"
__all__ = [
    'CheckOption',
]

from ..toolbox.deferred import Deferred
from .check_type import CheckType
from .key_value import KeyValue
from .error import OptionValidationError


class CheckOption(CheckType):
    """CheckOption(values)
       Check if key_value.value is in 'values'.
    """
    def __init__(self, values):
        self.values = values
        super().__init__()

    def check(self, key_value, section):
        values = [self.get_value(value, section) for value in self.values]
        if key_value.defined:
            if key_value.value not in values:
                raise OptionValidationError(
                    key_value,
                    "{!r} is not a valid option value; valid values are: ({})".format(key_value.value, ', '.join(repr(v) for v in values)))

    def self_validate(self, validator):
        for value in self.values:
            if not isinstance(value, Deferred):
                key_value = KeyValue(key='<option>', value=value, defined=True)
                validator.validate_key_value(key_value, section=None)
