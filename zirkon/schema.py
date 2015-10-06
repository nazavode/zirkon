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
Schema class.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'Schema',
]

from .config_base import ConfigBase
from .schema_section import SchemaSection
from .validator import ValidatorInstance


class Schema(ConfigBase, SchemaSection):  # pylint: disable=too-many-ancestors
    """Schema config class.

       Parameters
       ----------
       init: Mapping, optional
           some initial content
       dictionary: Mapping, optional
           the internal dictionary
       unexpected_option_validator: Validator, optional
           the validator to be used for unexpected options
       use_defaults: bool, optional
           if True, adds default values to defaults
           (defaults to True)
       self_validate: bool, optional

       Raises
       ------
       OptionValidationError
           on self-validation error
    """
    def __init__(self, init=None, *, dictionary=None, unexpected_option_validator=None,
                 use_defaults=True, self_validate=True):
        super().__init__(dictionary=dictionary, init=init, macros=True,
                         unexpected_option_validator=unexpected_option_validator,
                         use_defaults=use_defaults)
        if self_validate:
            schema_validator = self._subsection_class()(dictionary=None,
                                                        unexpected_option_validator=ValidatorInstance())
            schema_validator.validate(section=self, raise_on_error=True)

