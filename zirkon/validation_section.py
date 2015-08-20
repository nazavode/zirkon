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

"""
Implementation of the ValidationSection class, used to store validation errors.
"""

__author__ = "Simone Campagna"
__all__ = [
    'ValidationSection',
]

from .section import Section
from .validator.error import OptionValidationError


class ValidationSection(Section):
    """A Section to store ValidationResult values.
    """
    SUPPORTED_LIST_TYPES = ()
    SUPPORTED_SCALAR_TYPES = (OptionValidationError, )

    @classmethod
    def _subsection_class(cls):
        return ValidationSection

