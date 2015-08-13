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
config.validator.check
======================
Implementation of the Check base class
"""

__author__ = "Simone Campagna"
__all__ = [
    'Check',
]

import abc

from ..toolbox.deferred_eval import DeferredEval
from ..toolbox.deferred import Deferred


class Check(metaclass=abc.ABCMeta):
    """Check()
       Abstract base class for cheks. Checks must implement
       check(key_value, section) method.
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def check(self, key_value, section):
        """check(key_value, section)
           Run key/value check (can change key_value.value)
        """
        pass

    def has_actual_value(self, value):
        """has_actual_value(value)
           Return False if value is a DeferredEval or Deferred instance
        """
        return not isinstance(value, (DeferredEval, Deferred))

    def self_validate(self, validator):
        """self_validate(validator)
           Use validator to validate check's attributes.
        """
        pass

    def get_value(self, value, section):  # pylint: disable=R0201
        """get_value(value, section) -> value"""
        if section is not None:
            globals_d = {'SECTION': section, 'ROOT': section.root}
            if isinstance(value, DeferredEval):
                value = value(globals_d=globals_d)
            elif isinstance(value, Deferred):
                value = value.evaluate(globals_d=globals_d)
        return value
