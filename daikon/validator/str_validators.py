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
config.validator.str_validators
===============================
Implementation of the str validator classes
"""

__author__ = "Simone Campagna"
__all__ = [
    'Str',
    'StrOption',
    'StrList',
    'StrTuple',
]

from ..utils.compose import Composer

from .validator import Validator
from .sequence import Sequence
from .check_default import CheckDefault
from .check_range import CheckMinLen, CheckMaxLen
from .check_scalar import CheckStr
from .check_option import CheckOption
from .check_sequence import CheckList, CheckTuple


class Str(Validator):
    """Str()
       Validator for a str scalar key/value.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckStr, CheckMinLen, CheckMaxLen)


class StrOption(Validator):
    """StrOption()
       Validator for a str option key/value.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckStr, CheckOption)


class StrList(Sequence):
    """StrList()
       Validator for a str list key/value.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckList, CheckMinLen, CheckMaxLen)
    ITEM_VALIDATOR_CLASS = Str


class StrTuple(Sequence):
    """StrTuple()
       Validator for a str tuple key/value.
    """
    CHECK_COMPOSER = Composer(CheckDefault, CheckTuple, CheckMinLen, CheckMaxLen)
    ITEM_VALIDATOR_CLASS = Str
