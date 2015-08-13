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
daikon.config.schema
====================
"""

__author__ = "Simone Campagna"
__all__ = [
    'Schema',
]

from .config import Config
from .schema_section import SchemaSection


class Schema(Config, SchemaSection):  # pylint: disable=too-many-ancestors,I0011
    """Schema(init=None, *, dictionary=None)
       Schema config.
    """
    def __init__(self, init=None, *, dictionary=None, unexpected_parameter_validator=None):
        super().__init__(dictionary=dictionary, init=init)
        self.unexpected_parameter_validator = unexpected_parameter_validator

