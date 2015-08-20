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
Implementation of the UNDEFINED singleton.
"""

__author__ = "Simone Campagna"
__all__ = [
    'UNDEFINED',
]

from .singleton import Singleton


class UndefinedType(metaclass=Singleton):  # pylint: disable=R0903
    """UndefinedType singleton.
       To be used instead of None as placeholder where None is an acceptable value.
    """

    def __repr__(self):
        return "UNDEFINED"

UNDEFINED = UndefinedType()
