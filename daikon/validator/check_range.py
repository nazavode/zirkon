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

from .check import Check
from .error import MinValidationError, \
                   MaxValidationError, \
                   MinLenValidationError, \
                   MaxLenValidationError
from .key_value import KeyValue


class CheckRange(Check):
    """CheckRange(value)
       Base class for CheckMin, CheckMax.
    """

    ATTRIBUTE_NAME = None

    def auto_validate(self, validator):
        value = getattr(self, self.ATTRIBUTE_NAME)
        if value is not None:
            key = "<{}>".format(self.ATTRIBUTE_NAME)
            key_value = KeyValue(key=key, value=value, defined=True)
            validator.validate_key_value(key_value)

class CheckMin(CheckRange):
    """CheckMin(min=None)
       If min is not None, check if key/value is >= min.
    """
    ATTRIBUTE_NAME = 'min'

    def __init__(self, min=None):
        self.min = min
        super().__init__()

    def check(self, key_value):
        if self.min is not None:
            value = key_value.value
            if value < self.min:
                raise MinValidationError(key_value,
                                         "value {!r} is lower than min {!r}".format(value, self.min))


class CheckMax(CheckRange):
    """CheckMax(max=None)
       If max is not None, check if key/value is <= max.
    """
    ATTRIBUTE_NAME = 'max'

    def __init__(self, max=None):
        self.max = max
        super().__init__()

    def check(self, key_value):
        if self.max is not None:
            value = key_value.value
            if value > self.max:
                raise MaxValidationError(key_value,
                                         "value {!r} is greater than max {!r}".format(value, self.max))

class CheckMinLen(Check):
    """CheckMinLen(min_len=None)
       If min_len is not None, check if len of key/value is >= min_len.
    """

    def __init__(self, min_len=None):
        self.min_len = min_len
        super().__init__()

    def check(self, key_value):
        if self.min_len is not None:
            value = key_value.value
            if len(value) < self.min_len:
                raise MinLenValidationError(key_value,
                                            "value {!r} has length {} than is lower than min_len {!r}".format(
                                                value,
                                                len(value),
                                                self.min_len))


class CheckMaxLen(Check):
    """CheckMaxLen(max_len=None)
       If max_len is not None, check if len of key/value is <= max_len.
    """

    def __init__(self, max_len=None):
        self.max_len = max_len
        super().__init__()

    def check(self, key_value):
        if self.max_len is not None:
            value = key_value.value
            if len(value) > self.max_len:
                raise MaxLenValidationError(key_value,
                                            "value {!r} has length {} that is greater than max_len {!r}".format(
                                                value,
                                                len(value),
                                                self.max_len))
