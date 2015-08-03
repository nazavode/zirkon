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
config.validator.float_validator
================================
Implementation of the IntValidator classes
"""

__author__ = "Simone Campagna"
__all__ = [
    'FloatValidator',
    'FloatOptionValidator',
    'FloatListValidator',
    'FloatTupleValidator',
]

from ..utils.compose import Composer

from .validator import Validator
from .sequence_validator import SequenceValidator
from .check_default import CheckDefault
from .check_range import CheckMin, \
                         CheckMinLen, \
                         CheckMax, \
                         CheckMaxLen
from .check_scalar import CheckFloat
from .check_option import CheckOption
from .check_sequence import CheckList, \
                            CheckTuple


class FloatValidator(Validator):
    """FloatValidator()
       Validator for a float scalar key/value.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckFloat, CheckMin, CheckMax)

class FloatOptionValidator(Validator):
    """FloatValidator()
       Validator for a float option key/value.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckFloat, CheckOption)

class FloatListValidator(SequenceValidator):
    """FloatValidator()
       Validator for a float list key/value.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckList, CheckMinLen, CheckMaxLen)
    ITEM_VALIDATOR_CLASS = FloatValidator

class FloatTupleValidator(SequenceValidator):
    """FloatValidator()
       Validator for a float tuple key/value.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckTuple, CheckMinLen, CheckMaxLen)
    ITEM_VALIDATOR_CLASS = FloatValidator
