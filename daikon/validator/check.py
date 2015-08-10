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

from ..toolbox.unrepr import Deferred


class Check(metaclass=abc.ABCMeta):
    """Check()
       Abstract base class for cheks. Checks must implement
       check(key_value, section) method.
    """

    def __init__(self):
        pass

    def do_check(self, key_value, section):
        """do_check(key_value, section)
           Execute
           * convert(key_value);
           * check(key_value, section);
        """
        self.convert(key_value)
        self.check(key_value, section)

    @abc.abstractmethod
    def check(self, key_value, section):
        """check(key_value, section)
           Run key/value check (can change key_value.value)
        """
        pass

    def convert(self, key_value):
        """convert(key_value)
           Convert key/value (can change key_value.value)
        """
        pass

    def self_validate(self, validator):
        """self_validate(validator)
           Use validator to validate check's attributes.
        """
        pass

    def get_value(self, value, section):
        """get_value(value, section) -> value"""
        if section is not None and isinstance(value, Deferred):
            if section is not None:
                globals_d = {'SECTION': section, 'ROOT': section.root}
            else:
                globals_d = {}
            value = value(globals_d=globals_d)
        return value
  
