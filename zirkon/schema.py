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
zirkon.schema
=============
"""

__author__ = "Simone Campagna"
__all__ = [
    'Schema',
]

from .config_base import ConfigBase
from .schema_section import SchemaSection
from .validator import ValidatorInstance


class Schema(ConfigBase, SchemaSection):  # pylint: disable=too-many-ancestors,I0011
    """Schema(init=None, *, dictionary=None)
       Schema config.
    """
    def __init__(self, init=None, *, dictionary=None, unexpected_option_validator=None, self_validate=True):
        super().__init__(dictionary=dictionary, init=init, interpolation=True,
                         unexpected_option_validator=unexpected_option_validator)
        if self_validate:
            schema_validator = self._subsection_class()(dictionary=None,
                                                        unexpected_option_validator=ValidatorInstance())
            schema_validator.validate(section=self, raise_on_error=True)
