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
Implementation of the CheckChoice check class.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'CheckChoice',
]

from .check_type import CheckType
from .option import Option
from .error import InvalidChoiceError


class CheckChoice(CheckType):
    """Check if option.value is in 'choices'.

       Parameters
       ----------
       choices: tuple
           the set of accepted values

       Attributes
       ----------
       choices: tuple
           the set of accepted values
    """
    def __init__(self, choices):
        self.choices = choices
        super().__init__()

    def check(self, option, section):
        choices = [self.get_value(choice, section) for choice in self.choices]
        if option.defined:
            if option.value not in choices:
                raise InvalidChoiceError.build(
                    option,
                    "{!r} is not a valid choice; valid choices are: ({})".format(
                        option.value, ', '.join(repr(v) for v in choices)))

    def self_validate(self, validator):
        for choice in self.choices:
            if self.has_actual_value(choice):
                option = Option(name='<option>', value=choice, defined=True)
                validator.validate_option(option, section=None)
