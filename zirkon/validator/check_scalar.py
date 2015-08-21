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
Implementation of the CheckScalarType check classes.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'CheckScalarType',
    'CheckInt',
    'CheckFloat',
    'CheckStr',
    'CheckBool',
]

from .check_type import CheckType


class CheckScalarType(CheckType):
    """Checks if option has scalar type 'TYPE'.
    """
    pass


class CheckInt(CheckScalarType):
    """Checks if option has scalar type 'int'.
    """
    TYPE = int


class CheckFloat(CheckScalarType):
    """Checks if option has scalar type 'float' (int is accepted
       and converted to float).
    """
    TYPE = float
    SECONDARY_TYPES = (int, )


class CheckStr(CheckScalarType):
    """Checks if option has scalar type 'str'.
    """
    TYPE = str


class CheckBool(CheckScalarType):
    """Checks if option has scalar type 'bool' (int is accepted
       and converted to bool).
    """
    TYPE = bool
    SECONDARY_TYPES = (int, )

