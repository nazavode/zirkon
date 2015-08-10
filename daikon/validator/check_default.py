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
config.validator.check_default
==============================
Implementation of the CheckDefault class
"""

__author__ = "Simone Campagna"
__all__ = [
    'CheckDefault',
]

import copy

from ..toolbox.undefined import UNDEFINED
from ..toolbox.deferred import Deferred
from .check_required import CheckRequired
from .key_value import KeyValue


class CheckDefault(CheckRequired):
    """CheckDefault(default=UNDEFINED)
       Check if key/value is defined; if not:
       * if default is UNDEFINED, behaves like CheckRequired;
       * if default is not UNDEFINED, set key_value.value to default.
    """

    def __init__(self, default=UNDEFINED):
        self.default = default
        super().__init__()

    def check(self, key_value, section):
        if not key_value.defined:
            if self.default is UNDEFINED:
                super().check(key_value, section)
            else:
                key_value.value = copy.copy(self.get_value(self.default, section))
                key_value.defined = True

    def self_validate(self, validator):
        if self.default is not UNDEFINED and not isinstance(self.default, Deferred):
            key_value = KeyValue(key='<default>', value=self.default, defined=True)
            validator.validate_key_value(key_value, section=None)
