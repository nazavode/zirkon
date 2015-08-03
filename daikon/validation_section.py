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
validation_section
==================
Implementation of the SectionSchema class
"""

__author__ = "Simone Campagna"

import collections

from .section import Section
from .validator.error import ValidationError


class ValidationSection(Section):
    """ValidationSection(container, *, prefix='', init=None, unexpected_key_validator=None)
       A Section to store ValidationResult values.
    """
    SUPPORTED_VALUE_TYPES = (ValidationError, )

    @classmethod
    def subsection_class(cls):
        return ValidationSection
