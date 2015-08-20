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
Implementation of the CheckDefault check class.
"""

__author__ = "Simone Campagna"
__all__ = [
    'CheckDefault',
]

import copy

from ..toolbox.undefined import UNDEFINED
from .check_required import CheckRequired
from .option import Option


class CheckDefault(CheckRequired):
    """Checks if option is defined; if not:
       * if default is UNDEFINED, behaves like CheckRequired;
       * if default is not UNDEFINED, set option.value to default.

       Parameters
       ----------
       default: any, optional
           the default value
    """

    def __init__(self, default=UNDEFINED):
        self.default = default
        super().__init__()

    def check(self, option, section):
        if not option.defined:
            if self.default is UNDEFINED:
                super().check(option, section)
            else:
                option.value = copy.copy(self.get_value(self.default, section))
                option.defined = True

    def self_validate(self, validator):
        if (self.default is not UNDEFINED) and self.has_actual_value(self.default):
            option = Option(name='<default>', value=self.default, defined=True)
            validator.validate_option(option, section=None)
