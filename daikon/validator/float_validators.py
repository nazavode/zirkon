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
config.validator.float_validators
=================================
Implementation of the float validator classes
"""

__author__ = "Simone Campagna"
__all__ = [
    'Float',
    'FloatOption',
    'FloatList',
    'FloatTuple',
]

from ..toolbox.compose import Composer

from .validator import Validator
from .sequence import Sequence
from .check_default import CheckDefault
from .check_range import CheckMin, CheckMax, \
    CheckMinLen, CheckMaxLen

from .check_scalar import CheckFloat
from .check_option import CheckOption
from .check_sequence import CheckList, CheckTuple


class Float(Validator):
    """Float()
       Validator for a float scalar option.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckFloat, CheckMin, CheckMax)


class FloatOption(Validator):
    """FloatOption()
       Validator for a float option option.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckFloat, CheckOption)


class FloatList(Sequence):
    """FloatList()
       Validator for a float list option.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckList, CheckMinLen, CheckMaxLen)
    ITEM_VALIDATOR_CLASS = Float


class FloatTuple(Sequence):
    """FloatTuple()
       Validator for a float tuple option.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckTuple, CheckMinLen, CheckMaxLen)
    ITEM_VALIDATOR_CLASS = Float
