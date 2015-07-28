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


class CheckMin(Check):
    def __init__(self, min=None):
        self.min = min

    def check(self, key_value):
        if self.min is not None:
            value = key_value.value
            if value < self.min:
                raise MinValidationError(key_value, "value {!r} is lower than min {!r}".format(value, self.min))


class CheckMax(Check):
    def __init__(self, max=None):
        self.max = max

    def check(self, key_value):
        if self.max is not None:
            value = key_value.value
            if value > self.max:
                raise MaxValidationError(key_value, "value {!r} is greater than max {!r}".format(value, self.max))


class CheckMinLen(Check):
    def __init__(self, min_len=None):
        self.min_len = min_len

    def check(self, key_value):
        if self.min_len is not None:
            value = key_value.value
            if len(value) < self.min_len:
                raise MinLenValidationError(key_value, "value {!r} has length {} than is lower than min_len {!r}".format(
                    value,
                    len(value),
                    self.min_len))


class CheckMaxLen(Check):
    def __init__(self, max_len=None):
        self.max_len = max_len

    def check(self, key_value):
        if self.max_len is not None:
            value = key_value.value
            if len(value) > self.max_len:
                raise MaxLenValidationError(key_value, "value {!r} has length {} that is greater than max_len {!r}".format(
                    value,
                    len(value),
                    self.max_len))
