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
Implementation of the Int validator classes.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'Int',
    'IntChoice',
    'IntList',
    'IntTuple',
]

from ..toolbox.compose import Composer

from .validator import Validator
from .sequence import Sequence
from .check_default import CheckDefault
from .check_range import CheckMin, CheckMax, \
    CheckMinLen, CheckMaxLen

from .check_scalar import CheckInt
from .check_choice import CheckChoice
from .check_sequence import CheckList, CheckTuple


class Int(Validator):
    """Validator for a int scalar option."""
    CHECK_COMPOSER = Composer(CheckDefault, CheckInt, CheckMin, CheckMax)


class IntChoice(Validator):
    """Validator for a int option option."""
    CHECK_COMPOSER = Composer(CheckDefault, CheckInt, CheckChoice)


class IntList(Sequence):
    """Validator for a int list option."""
    CHECK_COMPOSER = Composer(CheckDefault, CheckList, CheckMinLen, CheckMaxLen)
    ITEM_VALIDATOR_CLASS = Int


class IntTuple(Sequence):
    """Validator for a int tuple option."""
    CHECK_COMPOSER = Composer(CheckDefault, CheckTuple, CheckMinLen, CheckMaxLen)
    ITEM_VALIDATOR_CLASS = Int

