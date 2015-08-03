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
section_schema
==============
Implementation of the SectionSchema class
"""

__author__ = "Simone Campagna"

import collections

from .section import Section
from .validation_section import ValidationSection
from .validator import ValidatorBase
from .validator.validator import Validator
from .validator.unexpected_parameter import UnexpectedParameter
from .validator.key_value import KeyValue
from .validator.error import ValidationError, \
    UnexpectedSectionValidationError, \
    UnexpectedParameterValidationError


class SectionSchema(Section):
    """SectionSchema(container, *, prefix='', init=None, unexpected_parameter_validator=None)
       Provides validation methods.
    """
    SUPPORTED_VALUE_TYPES = (str, ValidatorBase, )

    def __init__(self, container, *, prefix='', init=None, unexpected_parameter_validator=None, auto_validate=True):
        if unexpected_parameter_validator is None:
            unexpected_parameter_validator = UnexpectedParameter()
        self.unexpected_parameter_validator = unexpected_parameter_validator
        super().__init__(container=container, prefix=prefix, init=init)
        if auto_validate:
            schema_validator = self.subsection_class()(container=collections.OrderedDict(),
                                                       unexpected_parameter_validator=Validator(),
                                                       auto_validate=False)
            schema_validator.impl_validate(self, mode='load', ignore_errors=False)

    @classmethod
    def subsection_class(cls):
        return SectionSchema

    def subsection(self, prefix):
        return self.subsection_class()(container=self.container,
                                       unexpected_parameter_validator=self.unexpected_parameter_validator,
                                       prefix=prefix)

    @property
    def unexpected_parameter_validator(self):
        return self._unexpected_parameter_validator

    @unexpected_parameter_validator.setter
    def unexpected_parameter_validator(self, validator):
        if not isinstance(validator, ValidatorBase):
            raise TypeError("{!r} is not a ValidatorBase".format(validator))
        self._unexpected_parameter_validator = validator

    def validate(self, section, *, mode=None, ignore_errors=True):
        return self.impl_validate(section, mode=mode, ignore_errors=ignore_errors)

    def impl_validate(self, section, *, mode=None, ignore_errors=True, parent_fqname=''):
        validation_section = ValidationSection(container=collections.OrderedDict())
        # expected sub_sections:
        expected_sub_section_names = set()
        for sub_section_name, sub_section_schema in self.sections():
            expected_sub_section_names.add(sub_section_name)
            if section.has_parameter(sub_section_name):
                validation_section[sub_section_name] = UnexpectedParameterValidationError("unexpected parameter {} (expecting section)".format(key)) 
            else:
                if section.has_section(sub_section_name):
                    sub_section = section.get_section(sub_section_name)
                else:
                    sub_section = section.add_section(sub_section_name)
                sub_section_fqname = parent_fqname + sub_section_name + self.DOT
                sub_validation_section = sub_section_schema.impl_validate(section[sub_section_name],
                                                                         mode=mode,
                                                                         ignore_errors=ignore_errors,
                                                                         parent_fqname=sub_section_fqname)
                if sub_validation_section:
                    validation_section[sub_section_name] = sub_validation_section
        # unexpected sub_sections:
        unexpected_sub_section_names = set()
        for sub_section_name, sub_section in section.sections():
            if sub_section_name not in expected_sub_section_names:
                unexpected_sub_section_names.add(sub_section_name)
                sub_section_fqname = parent_fqname + sub_section_name + self.DOT
                sub_section_schema = self.subsection_class()(container=collections.OrderedDict(),
                                                             prefix=self.prefix,
                                                             unexpected_parameter_validator=self.unexpected_parameter_validator)
                sub_validation_section = sub_section_schema.impl_validate(section[sub_section_name],
                                                                         mode=mode,
                                                                         ignore_errors=ignore_errors,
                                                                         parent_fqname=sub_section_fqname)
                if sub_validation_section:
                    validation_section[sub_section_name] = sub_validation_section
        # expected parameters:
        expected_parameter_names = set()
        for parameter_name, validator in self.parameters():
            expected_parameter_names.add(parameter_name)
            key = parent_fqname + parameter_name
            if section.has_section(parameter_name):
                validation_section[parameter_name] = UnexpectedSectionValidationError("unexpected section {} (expecting parameter)".format(key)) 
            else:
                if section.has_parameter(parameter_name):
                    value = section.get_parameter(parameter_name)
                    defined = True
                else:
                    value = None
                    defined = False
                key_value = KeyValue(key=key, value=value, defined=defined)
                try:
                    validator.validate_key_value(key_value, mode=mode)
                except ValidationError as err:
                    validation_section[parameter_name] = err
                    if not ignore_errors:
                        raise
                else:
                    if not key_value.defined:
                        del section[parameter_name]
                    elif key_value.value is not value:
                        section[parameter_name] = key_value.value
        # unexpected parameters:
        unexpected_parameter_names = set()
        for parameter_name, parameter_value in section.parameters():
            if parameter_name not in expected_parameter_names:
                unexpected_parameter_names.add(parameter_name)
                validator = self.unexpected_parameter_validator
                key = parent_fqname + parameter_name
                key_value = KeyValue(key=key, value=parameter_value, defined=True)
                try:
                    validator.validate_key_value(key_value, mode=mode)
                except ValidationError as err:
                    validation_section[parameter_name] = err
                    if not ignore_errors:
                        raise
                else:
                    if not key_value.defined:
                        del section[parameter_name]
                    elif key_value.value is not parameter_value:
                        section[parameter_name] = key_value.value
        return validation_section
