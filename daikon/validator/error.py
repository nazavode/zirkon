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
OptionValidationError classes
"""

__author__ = "Simone Campagna"
__all__ = [
    'OptionValidationError',
    'InvalidContentError',
    'MissingRequiredOptionError',
    'UnexpectedSectionError',
    'UnexpectedOptionError',
    'InvalidTypeError',
    'InvalidValueError',
    'MinValueError',
    'MaxValueError',
    'InvalidChoiceError',
    'InvalidLengthError',
    'MinLengthError',
    'MaxLengthError',
]


class OptionValidationError(Exception):
    """OptionValidationError()
    """

    def __init__(self, option, message):
        self.option = option
        self.message = message
        super().__init__("{}: {}".format(option, message))

    def __reduce__(self):
        return (type(self), (self.option, self.message))


class InvalidContentError(OptionValidationError):
    """InvalidContentError()
    """
    pass


class InvalidTypeError(OptionValidationError):
    """InvalidTypeError()
    """
    pass


class InvalidValueError(OptionValidationError):
    """InvalidValueError()
    """
    pass


class MissingRequiredOptionError(InvalidContentError):
    """MissingRequiredOptionError()
    """
    pass


class UnexpectedSectionError(InvalidContentError):
    """UnexpectedSectionError()
    """
    pass


class UnexpectedOptionError(InvalidContentError):
    """UnexpectedOptionError()
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


class InvalidChoiceError(InvalidValueError):
    """InvalidChoiceError()
    """
    pass


class InvalidLengthError(OptionValidationError):
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


