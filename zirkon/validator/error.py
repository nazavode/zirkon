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
Implementation of the OptionValidationError classes.
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
    """OptionValidationError"""

    @classmethod
    def build(cls, option, message):
        """Builds an exception based on the option value.

           Parameters
           ----------
           option: Option
               the offending option
           message: str
               the error message

           Returns
           -------
           cls
               the exception
        """
        return cls("{}: {}".format(option, message))


class InvalidContentError(OptionValidationError):
    """InvalidContentError - option content is invalid"""
    pass


class InvalidTypeError(OptionValidationError):
    """InvalidTypeError - option type is invalid"""
    pass


class InvalidValueError(OptionValidationError):
    """InvalidValueError - option value is invalid"""
    pass


class MissingRequiredOptionError(InvalidContentError):
    """MissingRequiredOptionError - required option is missing"""
    pass


class UnexpectedSectionError(InvalidContentError):
    """UnexpectedSectionError - an unexpected section is found"""
    pass


class UnexpectedOptionError(InvalidContentError):
    """UnexpectedOptionError - an unexpected option is found"""
    pass


class MinValueError(InvalidValueError):
    """MinValueError - value is lower than allowed min"""
    pass


class MaxValueError(InvalidValueError):
    """MaxValueError - value is greater than allowed max"""
    pass


class InvalidChoiceError(InvalidValueError):
    """InvalidChoiceError - value is not an acceptable choice"""
    pass


class InvalidLengthError(OptionValidationError):
    """InvalidLengthError - value has an invalid length"""
    pass


class MinLengthError(InvalidLengthError):
    """MinLengthError - value length is lower than allowed min_len"""
    pass


class MaxLengthError(InvalidLengthError):
    """MaxLengthError - value length is greater than allowed max_len"""
    pass


