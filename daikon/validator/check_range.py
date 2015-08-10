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
config.validator.check_range
============================
Implementation of the CheckMin and CheckMax classes
"""

__author__ = "Simone Campagna"
__all__ = [
    'CheckMin',
    'CheckMax',
    'CheckMinLen',
    'CheckMaxLen',
]

from ..toolbox.deferred import Deferred
from .check import Check
from .error import MinValidationError, \
    MaxValidationError, \
    MinLenValidationError, \
    MaxLenValidationError

from .key_value import KeyValue


class CheckRange(Check):  # pylint: disable=W0223
    """CheckRange(value)
       Base class for CheckMin, CheckMax.
    """

    ATTRIBUTE_NAME = None

    def self_validate(self, validator):
        value = getattr(self, self.ATTRIBUTE_NAME)
        if value is not None and not isinstance(value, Deferred):
            key = "<{}>".format(self.ATTRIBUTE_NAME)
            key_value = KeyValue(key=key, value=value, defined=True)
            validator.validate_key_value(key_value, section=None)


class CheckMin(CheckRange):
    """CheckMin(min=None)
       If min is not None, check if key/value is >= min.
    """
    ATTRIBUTE_NAME = 'min'

    def __init__(self, min=None):  # pylint: disable=W0622
        self.min = min
        super().__init__()

    def check(self, key_value, section):
        min_value = self.get_value(self.min, section)
        if min_value is not None:
            value = key_value.value
            if value < min_value:
                raise MinValidationError(key_value,
                                         "value {!r} is lower than min {!r}".format(value, min_value))


class CheckMax(CheckRange):
    """CheckMax(max=None)
       If max is not None, check if key/value is <= max.
    """
    ATTRIBUTE_NAME = 'max'

    def __init__(self, max=None):  # pylint: disable=W0622
        self.max = max
        super().__init__()

    def check(self, key_value, section):
        max_value = self.get_value(self.max, section)
        if max_value is not None:
            value = key_value.value
            if value > max_value:
                raise MaxValidationError(key_value,
                                         "value {!r} is greater than max {!r}".format(value, max_value))


class CheckMinLen(Check):
    """CheckMinLen(min_len=None)
       If min_len is not None, check if len of key/value is >= min_len.
    """

    def __init__(self, min_len=None):
        self.min_len = min_len
        super().__init__()

    def check(self, key_value, section):
        min_len_value = self.get_value(self.min_len, section)
        if min_len_value is not None:
            value = key_value.value
            if len(value) < min_len_value:
                raise MinLenValidationError(key_value,
                                            "value {!r} has length {} than is lower than min_len {!r}".format(
                                                value,
                                                len(value),
                                                min_len_value))


class CheckMaxLen(Check):
    """CheckMaxLen(max_len=None)
       If max_len is not None, check if len of key/value is <= max_len.
    """

    def __init__(self, max_len=None):
        self.max_len = max_len
        super().__init__()

    def check(self, key_value, section):
        max_len_value = self.get_value(self.max_len, section)
        if max_len_value is not None:
            value = key_value.value
            if len(value) > max_len_value:
                raise MaxLenValidationError(key_value,
                                            "value {!r} has length {} that is greater than max_len {!r}".format(
                                                value,
                                                len(value),
                                                max_len_value))
