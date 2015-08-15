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
from .validator.complain import Complain
from .validator.option import Option
from .validator.error import OptionValidationError, \
    UnexpectedSectionError, \
    UnexpectedOptionError


def _validate_option(*, validator, section, validation_section,
                     option_name, raise_on_error, option):
    """_validate_option(*, ...)
       Validates an option and uses the validation result to
       eventually change the option value.
       Used to implement SchemaSection.impl_validate(...) method.
    """
    value = option.value
    try:
        validator.validate_option(option, section)
    except OptionValidationError as err:
        validation_section[option_name] = err
        if raise_on_error:
            raise
    else:
        if not option.defined:
            del section[option_name]
        elif option.value is not value:
            section[option_name] = option.value


class SchemaSection(Section):
    """SchemaSection(init=None, *, dictionary=None, parent=None,
                     unexpected_option_validator=None,
                     self_validate=True)
       A Section class to perform validation. All values must be Validator
       instances.

       The 'unexpected_option_validator' is used to validate unexpected
       options (options found in the section to be validated, but not
       in the schema). By default it is 'Complain()', which
       raises an UnexpectedOptionError. The 'Ignore()' validator
       can be used to ignore unexpected options (they will be kept in
       the validated section), while the 'Remove()' validator can be used
       to remove unexpected options from the validated section.
    """
    SUPPORTED_LIST_TYPES = ()
    SUPPORTED_SCALAR_TYPES = (Validator, )

    def __init__(self, init=None, *, dictionary=None, parent=None,
                 unexpected_option_validator=None,
                 self_validate=True):
        self._unexpected_option_validator = None
        self.unexpected_option_validator = unexpected_option_validator
        super().__init__(dictionary=dictionary, init=init, parent=parent)
        if self_validate:
            schema_validator = self._subsection_class()(dictionary=None,
                                                        unexpected_option_validator=ValidatorInstance(),
                                                        self_validate=False)
            schema_validator.validate(section=self, raise_on_error=True)

    @classmethod
    def _subsection_class(cls):
        return SchemaSection

    def _subsection(self, section_name, dictionary):
        return self._subsection_class()(dictionary=dictionary,
                                        unexpected_option_validator=self.unexpected_option_validator)

    @property
    def unexpected_option_validator(self):
        """unexpected_option_validator [property getter]
           Returns the validator to be used for unexpected options.
        """
        return self._unexpected_option_validator

    @unexpected_option_validator.setter
    def unexpected_option_validator(self, validator):
        """unexpected_option_validator [property setter]
           Sets the validator to be used for unexpected options.
        """
        if validator is None:
            validator = Complain()
        if not isinstance(validator, Validator):
            raise TypeError("{!r} is not a Validator".format(validator))
        self._unexpected_option_validator = validator

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
        self.impl_validate_options(section=section, validation_section=validation_section, **args)
        self.impl_validate_subsections(section=section, validation_section=validation_section, **args)

    def impl_validate_subsections(self, *, section, validation_section, raise_on_error=False, parent_fqname=''):
        """impl_validate_subsections(...)
           Validate subsections.
        """
        # expected subsections:
        expected_subsection_names = set()
        for subsection_name, schema_subsection in self.sections():
            expected_subsection_names.add(subsection_name)
            if section.has_option(subsection_name):
                validation_section[subsection_name] = UnexpectedOptionError(
                    "unexpected option {} (expecting section)".format(subsection_name))
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
                schema_subsection = self._subsection_class()(
                    unexpected_option_validator=self.unexpected_option_validator)
                sub_validation_section = ValidationSection()
                schema_subsection.impl_validate(
                    section[subsection_name],
                    validation_section=sub_validation_section,
                    raise_on_error=raise_on_error,
                    parent_fqname=subsection_fqname)
                if sub_validation_section:
                    validation_section[subsection_name] = sub_validation_section

    def impl_validate_options(self, *, section, validation_section, raise_on_error=False, parent_fqname=''):
        """impl_validate_options(...)
           Validate options.
        """
        # expected options:
        expected_option_names = set()
        for option_name, validator in list(self.options()):
            expected_option_names.add(option_name)
            fqname = parent_fqname + option_name
            if section.has_section(option_name):
                validation_section[option_name] = UnexpectedSectionError(
                    "unexpected section {} (expecting option)".format(fqname))
            else:
                if section.has_option(option_name):
                    value = section.get_option(option_name)
                    defined = True
                else:
                    value = None
                    defined = False
                option = Option(name=fqname, value=value, defined=defined)
                _validate_option(
                    validator=validator,
                    section=section,
                    validation_section=validation_section,
                    option_name=option_name,
                    option=option,
                    raise_on_error=raise_on_error)
        # unexpected options:
        for option_name, option_value in list(section.options()):
            if option_name not in expected_option_names:
                validator = self.unexpected_option_validator
                fqname = parent_fqname + option_name
                option = Option(name=fqname, value=option_value, defined=True)
                _validate_option(
                    validator=validator,
                    validation_section=validation_section,
                    section=section,
                    option_name=option_name,
                    option=option,
                    raise_on_error=raise_on_error)
