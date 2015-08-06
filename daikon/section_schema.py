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
from .validator import Validator, ValidatorInstance
from .validator.unexpected_parameter import UnexpectedParameter
from .validator.key_value import KeyValue
from .validator.error import ValidationError, \
    UnexpectedSectionValidationError, \
    UnexpectedParameterValidationError


def _validate_parameter(*, validator, section, validation_section,
                        parameter_name, raise_on_error, key_value):
    """_validate_parameter(*, ...)
       Validates a parameter and uses the validation result to
       eventually change the parameter value.
       Used to implement SectionSchema.impl_validate() method.
    """
    value = key_value.value
    try:
        validator.validate_key_value(key_value)
    except ValidationError as err:
        validation_section[parameter_name] = err
        if raise_on_error:
            raise
    else:
        if not key_value.defined:
            del section[parameter_name]
        elif key_value.value is not value:
            section[parameter_name] = key_value.value


class SectionSchema(Section):
    """SectionSchema(container, *, prefix='', init=None,
                     unexpected_parameter_validator=UnexpectedParameter(),
                     auto_validate=True)
       A Section class to perform validation. All values must be Validator
       instances.

       The 'unexpected_parameter_validator' is used to validate unexpected
       parameters (parameters found in the section to be validated, but not
       in the schema). By default it is 'UnexpectedParameter()', which
       raises an UnexpectedParameterValidationError. The 'Ignore()' validator
       can be used to ignore unexpected parameters (they will be kept in
       the validated section), while the 'Remove()' validator can be used
       to remove unexpected parameters from the validated section.
    """
    SUPPORTED_VALUE_TYPES = (str, Validator)

    def __init__(self, container, *, prefix='', init=None,
                 unexpected_parameter_validator=UnexpectedParameter(),
                 auto_validate=True):
        self._unexpected_parameter_validator = None
        self.unexpected_parameter_validator = unexpected_parameter_validator
        super().__init__(container=container, prefix=prefix, init=init)
        if auto_validate:
            schema_validator = self.subsection_class()(container=collections.OrderedDict(),
                                                       unexpected_parameter_validator=ValidatorInstance(),
                                                       auto_validate=False)
            schema_validator.impl_validate(self, raise_on_error=True)

    @classmethod
    def subsection_class(cls):
        return SectionSchema

    def subsection(self, prefix):
        return self.subsection_class()(container=self.container,
                                       unexpected_parameter_validator=self.unexpected_parameter_validator,
                                       prefix=prefix)

    @property
    def unexpected_parameter_validator(self):
        """unexpected_parameter_validator [property getter]
           Returns the validator to be used for unexpected parameters.
        """
        return self._unexpected_parameter_validator

    @unexpected_parameter_validator.setter
    def unexpected_parameter_validator(self, validator):
        """unexpected_parameter_validator [property setter]
           Sets the validator to be used for unexpected parameters.
        """
        if not isinstance(validator, Validator):
            raise TypeError("{!r} is not a Validator".format(validator))
        self._unexpected_parameter_validator = validator

    def validate(self, section, *, raise_on_error=False):
        """validate(section, *, raise_on_error=False) -> validation section
           Validates 'section' and returns a ValidationSection with the found
           validation errors.
           If 'raise_on_error', the first validation error is fatal.
        """
        return self.impl_validate(section, raise_on_error=raise_on_error)

    def impl_validate(self, section, *, raise_on_error=False, parent_fqname=''):
        """impl_validate(section, *, raise_on_error=False, parent_fqname='') ->
               validation section
           Implementation of the validate method.
        """
        validation_section = ValidationSection(container=collections.OrderedDict())
        args = dict(raise_on_error=raise_on_error, parent_fqname=parent_fqname)
        self.impl_validate_subsections(section=section, validation_section=validation_section, **args)
        self.impl_validate_parameters(section=section, validation_section=validation_section, **args)
        return validation_section

    def impl_validate_subsections(self, *, section, validation_section, raise_on_error=False, parent_fqname=''):
        """impl_validate_subsections(...)
           Validate subsections.
        """
        # expected subsections:
        expected_subsection_names = set()
        for subsection_name, subsection_schema in self.sections():
            expected_subsection_names.add(subsection_name)
            if section.has_parameter(subsection_name):
                validation_section[subsection_name] = UnexpectedParameterValidationError(
                    "unexpected parameter {} (expecting section)".format(subsection_name))
            else:
                if section.has_section(subsection_name):
                    subsection = section.get_section(subsection_name)
                else:
                    subsection = section.add_section(subsection_name)
                subsection_fqname = parent_fqname + subsection_name + self.DOT
                sub_validation_section = subsection_schema.impl_validate(
                    subsection,
                    raise_on_error=raise_on_error,
                    parent_fqname=subsection_fqname)
                if sub_validation_section:
                    validation_section[subsection_name] = sub_validation_section
        # unexpected subsections:
        for subsection_name, subsection in section.sections():
            if subsection_name not in expected_subsection_names:
                subsection_fqname = parent_fqname + subsection_name + self.DOT
                subsection_schema = self.subsection_class()(
                    container=collections.OrderedDict(),
                    prefix=self.prefix,
                    unexpected_parameter_validator=self.unexpected_parameter_validator)
                sub_validation_section = subsection_schema.impl_validate(
                    section[subsection_name],
                    raise_on_error=raise_on_error,
                    parent_fqname=subsection_fqname)
                if sub_validation_section:
                    validation_section[subsection_name] = sub_validation_section

    def impl_validate_parameters(self, *, section, validation_section, raise_on_error=False, parent_fqname=''):
        """impl_validate_parameters(...)
           Validate parameters.
        """
        # expected parameters:
        expected_parameter_names = set()
        for parameter_name, validator in self.parameters():
            expected_parameter_names.add(parameter_name)
            key = parent_fqname + parameter_name
            if section.has_section(parameter_name):
                validation_section[parameter_name] = UnexpectedSectionValidationError(
                    "unexpected section {} (expecting parameter)".format(key))
            else:
                if section.has_parameter(parameter_name):
                    value = section.get_parameter(parameter_name)
                    defined = True
                else:
                    value = None
                    defined = False
                key_value = KeyValue(key=key, value=value, defined=defined)
                _validate_parameter(
                    validator=validator,
                    section=section,
                    validation_section=validation_section,
                    parameter_name=parameter_name,
                    key_value=key_value,
                    raise_on_error=raise_on_error)
        # unexpected parameters:
        for parameter_name, parameter_value in section.parameters():
            if parameter_name not in expected_parameter_names:
                validator = self.unexpected_parameter_validator
                key = parent_fqname + parameter_name
                key_value = KeyValue(key=key, value=parameter_value, defined=True)
                _validate_parameter(
                    validator=validator,
                    validation_section=validation_section,
                    section=section,
                    parameter_name=parameter_name,
                    key_value=key_value,
                    raise_on_error=raise_on_error)
