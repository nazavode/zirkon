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
config.validator.bool_validators
================================
Implementation of the Bool classes
"""

__author__ = "Simone Campagna"
__all__ = [
    'Bool',
    'BoolOption',
    'BoolList',
    'BoolTuple',
]

from ..toolbox.compose import Composer

from .validator import Validator
from .sequence import Sequence
from .check_default import CheckDefault
from .check_range import CheckMinLen, CheckMaxLen

from .check_scalar import CheckBool
from .check_option import CheckOption
from .check_sequence import CheckList, CheckTuple


class Bool(Validator):
    """Bool()
       Validator for a scalar bool option.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckBool)


class BoolOption(Validator):
    """BoolOption()
       Validator for a bool option option.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckBool, CheckOption)


class BoolList(Sequence):
    """BoolList()
       Validator for a bool list option.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckList, CheckMinLen, CheckMaxLen)
    ITEM_VALIDATOR_CLASS = Bool


class BoolTuple(Sequence):
    """BoolTuple()
       Validator for a bool tuple option.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckTuple, CheckMinLen, CheckMaxLen)
    ITEM_VALIDATOR_CLASS = Bool
