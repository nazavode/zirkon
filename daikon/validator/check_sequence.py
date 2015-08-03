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
config.validator.check_sequence
===============================
Implementation of the CheckList, CheckTuple classes
"""

__author__ = "Simone Campagna"
__all__ = [
    'CheckSequenceType',
    'CheckList',
    'CheckTuple',
]

from .check_type import CheckType
from .key_value import KeyValue


class CheckSequenceType(CheckType):
    """CheckSequenceType()
       Base class for CheckList, CheckTuple.
    """

class CheckList(CheckSequenceType):
    """CheckList()
       Check if key/value is a list.
    """
    TYPE = list

class CheckTuple(CheckSequenceType):
    """CheckList()
       Check if key/value is a tuple.
    """
    TYPE = tuple
