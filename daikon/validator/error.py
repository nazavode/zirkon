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
config.validator.error
======================
ValidationError classes
"""

__author__ = "Simone Campagna"
__all__ = [
    'ValidationError',
    'InvalidContentError',
    'MissingRequiredParameterError',
    'UnexpectedSectionError',
    'UnexpectedParameterError',
    'InvalidTypeError',
    'InvalidValueError',
    'MinValueError',
    'MaxValueError',
    'OptionValueError',
    'InvalidLengthError',
    'MinLengthError',
    'MaxLengthError',
]


class ValidationError(Exception):
    """ValidationError()
    """

    def __init__(self, key_value, message):
        self.key_value = key_value
        super().__init__("{}: {}".format(key_value, message))


class InvalidContentError(ValidationError):
    """InvalidContentError()
    """
    pass


class InvalidTypeError(ValidationError):
    """InvalidTypeError()
    """
    pass


class InvalidValueError(ValidationError):
    """InvalidValueError()
    """
    pass


class MissingRequiredParameterError(InvalidContentError):
    """MissingRequiredParameterError()
    """
    pass


class UnexpectedSectionError(InvalidContentError):
    """UnexpectedSectionError()
    """
    pass


class UnexpectedParameterError(InvalidContentError):
    """UnexpectedParameterError()
    """
    pass


class MinValueError(InvalidValueError):
    """MinValueError()
    """
    pass


class MaxValueError(InvalidValueError):
    """MaxValueError()
    """
    pass


class OptionValueError(InvalidValueError):
    """OptionValueError()
    """
    pass


class InvalidLengthError(ValidationError):
    """InvalidLengthError()
    """
    pass


class MinLengthError(InvalidLengthError):
    """MinLengthError()
    """
    pass


class MaxLengthError(InvalidLengthError):
    """MaxLengthError()
    """
    pass


