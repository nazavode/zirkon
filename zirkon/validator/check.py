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
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'Check',
]

import abc

from ..toolbox.macro import Macro


class Check(metaclass=abc.ABCMeta):
    """Abstract base class for cheks. Checks must implement
       check(option, section) method.
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def check(self, option, section):
        """check(option, section)
           Run option check (can change option.value, option.defined)

           Parameters
           ----------
           option: |Option|
               the option to be checked
           section: |Section|
               the containing section

           Raises
           ------
           |OptionValidationError|
               validation error
        """
        raise NotImplementedError

    def has_actual_value(self, value):  # pylint: disable=no-self-use
        """Returns True if value is not a Macro instance.

           Parameters
           ----------
           value: |any|
               the value

           Returns
           -------
           bool
               True if value is immediately available (i.e. it is not a Macro).
        """
        return not isinstance(value, Macro)

    def self_validate(self, validator):
        """Uses validator to validate check's attributes.

           Parameters
           ----------
           validator: zirkon.validator.Validator
               the validator containing this check
        """
        pass

    def get_value(self, value, section):  # pylint: disable=no-self-use
        """Returns an evaluated value

           Parameters
           ----------
           value: |any|
               the original value
           section: |Section|
               the containing section

           Returns
           -------
           |any|
               the evaluated value
        """
        if section is not None:
            value = section.evaluate_option_value(value)
        return value
