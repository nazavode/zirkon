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
config.validator.bool_validator
===============================
Implementation of the BoolValidator classes
"""

__author__ = "Simone Campagna"
__all__ = [
    'BoolValidator',
    'BoolOptionValidator',
    'BoolListValidator',
    'BoolTupleValidator',
]

from ..utils.compose import Composer

from .validator import Validator
from .sequence_validator import SequenceValidator
from .check_default import CheckDefault
from .check_range import CheckMinLen, CheckMaxLen

from .check_scalar import CheckBool
from .check_option import CheckOption
from .check_sequence import CheckList, CheckTuple


class BoolValidator(Validator):
    """BoolValidator()
       Validator for a scalar bool key/value.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckBool)


class BoolOptionValidator(Validator):
    """BoolValidator()
       Validator for a bool option key/value.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckBool, CheckOption)


class BoolListValidator(SequenceValidator):
    """BoolValidator()
       Validator for a bool list key/value.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckList, CheckMinLen, CheckMaxLen)
    ITEM_VALIDATOR_CLASS = BoolValidator


class BoolTupleValidator(SequenceValidator):
    """BoolValidator()
       Validator for a bool tuple key/value.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckTuple, CheckMinLen, CheckMaxLen)
    ITEM_VALIDATOR_CLASS = BoolValidator
