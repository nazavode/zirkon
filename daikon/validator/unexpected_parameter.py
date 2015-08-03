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
config.validator.unexpected_parameter
=====================================
Implementation of the UnexpectedParameter class
"""

__author__ = "Simone Campagna"
__all__ = [
    'UnexpectedParameter',
]

from ..utils.compose import Composer

from .validator_base import ValidatorBase
from .check_unexpected_parameter import CheckUnexpectedParameter


class UnexpectedParameter(ValidatorBase):
    """UnexpectedParameter()
       Validator for unexpected parameters
    """
    CHECK_COMPOSER = Composer(CheckUnexpectedParameter)
