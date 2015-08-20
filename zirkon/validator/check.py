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
Implementation of the Check base class.
"""

__author__ = "Simone Campagna"
__all__ = [
    'Check',
]

import abc

from ..toolbox.deferred import Deferred


class Check(metaclass=abc.ABCMeta):
    """Check()
       Abstract base class for cheks. Checks must implement
       check(option, section) method.
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def check(self, option, section):
        """check(option, section)
           Run option check (can change option.value, option.defined)
        """
        raise NotImplementedError

    def has_actual_value(self, value):  # pylint: disable=R0201
        """has_actual_value(value)
           Return False if value is a Deferred instance
        """
        return not isinstance(value, Deferred)

    def self_validate(self, validator):
        """self_validate(validator)
           Use validator to validate check's attributes.
        """
        pass

    def get_value(self, value, section):  # pylint: disable=R0201
        """get_value(value, section) -> value"""
        if section is not None:
            value = section.evaluate_option_value(value)
        return value
