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
daikon.schema_section
=====================
Implementation of the SchemaSection class
"""

__author__ = "Simone Campagna"
__all__ = [
    'SchemaSection',
]

from .section import Section
from .validation_section import ValidationSection
from .validation import Validation
from .validator import Validator, ValidatorInstance
from .validator.unexpected_parameter import UnexpectedParameter
from .validator.key_value import KeyValue
from .validator.error import KeyValidationError, \
    UnexpectedSectionError, \
    UnexpectedParameterError


def _validate_parameter(*, validator, section, validation_section,
                        parameter_name, raise_on_error, key_value):
    """_validate_parameter(*, ...)
       Validates a parameter and uses the validation result to
       eventually change the parameter value.
       Used to implement SchemaSection.impl_validate(...) method.
    """
    value = key_value.value
    try:
        validator.validate_key_value(key_value, section)
    except KeyValidationError as err:
        validation_section[parameter_name] = err
        if raise_on_error:
            raise
    else:
        if not key_value.defined:
            del section[parameter_name]
        elif key_value.value is not value:
            section[parameter_name] = key_value.value


class SchemaSection(Section):
    """SchemaSection(*, dictionary=None, init=None,
                     unexpected_parameter_validator=UnexpectedParameter(),
                     self_validate=True)
       A Section class to perform validation. All values must be Validator
       instances.

       The 'unexpected_parameter_validator' is used to validate unexpected
       parameters (parameters found in the section to be validated, but not
       in the schema). By default it is 'UnexpectedParameter()', which
       raises an UnexpectedParameterError. The 'Ignore()' validator
       can be used to ignore unexpected parameters (they will be kept in
       the validated section), while the 'Remove()' validator can be used
       to remove unexpected parameters from the validated section.
    """
    SUPPORTED_LIST_TYPES = ()
    SUPPORTED_SCALAR_TYPES = (Validator, )

    def __init__(self, *, dictionary=None, init=None, parent=None,
                 unexpected_parameter_validator=UnexpectedParameter(),
                 self_validate=True):
        self._unexpected_parameter_validator = None
        self.unexpected_parameter_validator = unexpected_parameter_validator
        super().__init__(dictionary=dictionary, init=init, parent=parent)
        if self_validate:
            schema_validator = self.subsection_class()(dictionary=None,
                                                       unexpected_parameter_validator=ValidatorInstance(),
                                                       self_validate=False)
            schema_validator.validate(section=self, raise_on_error=True)

    @classmethod
    def subsection_class(cls):
        return SchemaSection

    def subsection(self, dictionary):
        return self.subsection_class()(dictionary=dictionary,
                                       unexpected_parameter_validator=self.unexpected_parameter_validator)

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

    def validate(self, section, *, validation=None, raise_on_error=False):
        """validate(section, *, validation=None, raise_on_error=False) -> validation object
           Validates 'section' and returns a ValidationSection with the found
           validation errors.
           If 'raise_on_error', the first validation error is fatal.
        """
        if validation is None:
            validation = Validation()
        self.impl_validate(
            section=section,
            validation_section=validation,
            raise_on_error=raise_on_error)
        return validation

    def impl_validate(self, section, validation_section, *, raise_on_error=False, parent_fqname=''):
        """impl_validate(section, validation_section, *, raise_on_error=False, parent_fqname='')
           Implementation of the validate method.
        """
        args = dict(raise_on_error=raise_on_error, parent_fqname=parent_fqname)
        self.impl_validate_parameters(section=section, validation_section=validation_section, **args)
        self.impl_validate_subsections(section=section, validation_section=validation_section, **args)

    def impl_validate_subsections(self, *, section, validation_section, raise_on_error=False, parent_fqname=''):
        """impl_validate_subsections(...)
           Validate subsections.
        """
        # expected subsections:
        expected_subsection_names = set()
        for subsection_name, schema_subsection in self.sections():
            expected_subsection_names.add(subsection_name)
            if section.has_parameter(subsection_name):
                validation_section[subsection_name] = UnexpectedParameterError(
                    "unexpected parameter {} (expecting section)".format(subsection_name))
            else:
                if section.has_section(subsection_name):
                    subsection = section.get_section(subsection_name)
                else:
                    subsection = section.add_section(subsection_name)
                subsection_fqname = parent_fqname + subsection_name + '.'
                sub_validation_section = ValidationSection()
                schema_subsection.impl_validate(
                    subsection,
                    validation_section=sub_validation_section,
                    raise_on_error=raise_on_error,
                    parent_fqname=subsection_fqname)
                if sub_validation_section:
                    validation_section[subsection_name] = sub_validation_section
        # unexpected subsections:
        for subsection_name, subsection in section.sections():
            if subsection_name not in expected_subsection_names:
                subsection_fqname = parent_fqname + subsection_name + '.'
                schema_subsection = self.subsection_class()(
                    unexpected_parameter_validator=self.unexpected_parameter_validator)
                sub_validation_section = ValidationSection()
                schema_subsection.impl_validate(
                    section[subsection_name],
                    validation_section=sub_validation_section,
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
        for parameter_name, validator in list(self.parameters()):
            expected_parameter_names.add(parameter_name)
            key = parent_fqname + parameter_name
            if section.has_section(parameter_name):
                validation_section[parameter_name] = UnexpectedSectionError(
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
        for parameter_name, parameter_value in list(section.parameters()):
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
