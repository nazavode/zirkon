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
    'UndefinedKeyValidationError',
    'TypeValidationError',
    'MinValidationError',
    'MaxValidationError',
    'MinLenValidationError',
    'MaxLenValidationError',
    'InvalidOptionValidationError',
]

class ValidationError(Exception):
    """ValidationError()
    """

    def __init__(self, key_value, message):
        self.key_value = key_value
        super().__init__("{}: {}".format(key_value, message))

class UndefinedKeyValidationError(ValidationError):
    """UndefinedValidationError()
    """
    pass

class TypeValidationError(ValidationError):
    """RangeValidationError()
    """
    pass

class MinValidationError(ValidationError):
    """MinValidationError()
    """
    pass

class MaxValidationError(ValidationError):
    """MaxValidationError()
    """
    pass

class MinLenValidationError(ValidationError):
    """MinLenValidationError()
    """
    pass

class MaxLenValidationError(ValidationError):
    """MaxLenValidationError()
    """
    pass

class InvalidOptionValidationError(ValidationError):
    """InvalidOptionValidationError()
    """
    pass

