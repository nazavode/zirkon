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
Implementation of the CheckMin, CheckMax, CheckMinLen, CheckMaxLen check classes.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'CheckMin',
    'CheckMax',
    'CheckMinLen',
    'CheckMaxLen',
]

from .check import Check
from .error import MinValueError, \
    MaxValueError, \
    MinLengthError, \
    MaxLengthError

from .option import Option


class CheckRange(Check):  # pylint: disable=W0223
    """Base class for CheckMin, CheckMax, CheckMinLen, CheckMaxLen."""

    ATTRIBUTE_NAME = None

    def self_validate(self, validator):
        value = getattr(self, self.ATTRIBUTE_NAME)
        if (value is not None) and self.has_actual_value(value):
            name = "<{}>".format(self.ATTRIBUTE_NAME)
            option = Option(name=name, value=value, defined=True)
            validator.validate_option(option, section=None)


class CheckMin(CheckRange):
    """Checks if value is >= min.

       Parameters
       ----------
       min: |any|, optional
           the min value
    """
    ATTRIBUTE_NAME = 'min'

    def __init__(self, min=None):  # pylint: disable=W0622
        self.min = min
        super().__init__()

    def check(self, option, section):
        min_value = self.get_value(self.min, section)
        if min_value is not None:
            value = option.value
            if value < min_value:
                raise MinValueError.build(
                    option,
                    "value is lower than min {!r}".format(min_value))


class CheckMax(CheckRange):
    """Checks if value is <= max.

       Parameters
       ----------
       max: |any|, optional
           the max value

       Attributes
       ----------
       max: |any|, optional
           the max value
    """
    ATTRIBUTE_NAME = 'max'

    def __init__(self, max=None):  # pylint: disable=W0622
        self.max = max
        super().__init__()

    def check(self, option, section):
        max_value = self.get_value(self.max, section)
        if max_value is not None:
            value = option.value
            if value > max_value:
                raise MaxValueError.build(
                    option,
                    "value is greater than max {!r}".format(max_value))


class CheckMinLen(Check):
    """Checks if value length is >= min_len.

       Parameters
       ----------
       min_len: |any|, optional
           the min length

       Attributes
       ----------
       min_len: |any|, optional
           the min length
    """

    def __init__(self, min_len=None):
        self.min_len = min_len
        super().__init__()

    def check(self, option, section):
        min_len_value = self.get_value(self.min_len, section)
        if min_len_value is not None:
            value = option.value
            if len(value) < min_len_value:
                raise MinLengthError.build(
                    option,
                    "length {} is lower than min_len {!r}".format(
                        len(value),
                        min_len_value))


class CheckMaxLen(Check):
    """Checks if value length is >= max_len.

       Parameters
       ----------
       max_len: |any|, optional
           the max length

       Attributes
       ----------
       max_len: |any|, optional
           the max length
    """

    def __init__(self, max_len=None):
        self.max_len = max_len
        super().__init__()

    def check(self, option, section):
        max_len_value = self.get_value(self.max_len, section)
        if max_len_value is not None:
            value = option.value
            if len(value) > max_len_value:
                raise MaxLengthError.build(
                    option,
                    "length {} is greater than max_len {!r}".format(
                        len(value),
                        max_len_value))
