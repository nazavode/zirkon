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
Implementation of the SchemaSection class, implementing the validate method.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'SchemaSection',
]

from .section import Section
from .config_section import ConfigSection
from .validation_section import ValidationSection
from .validation import Validation
from .validator import Validator
from .validator.complain import Complain
from .validator.option import Option
from .validator.error import OptionValidationError, \
    UnexpectedSectionError, \
    UnexpectedOptionError


def _reset_option_default(*, section, option, option_name):
    """Check if the option value is from defaults; if so, it is removed.
       This is to force re-evaluation of macros in validator default.
    """
    section_defaults = section
    if isinstance(section, ConfigSection):
        defaults = section.defaults
        if defaults is not None:
            section_defaults = defaults
            if option.defined:
                for key, _ in section.options():
                    if key == option_name:
                        # option is from standard values
                        break
                else:
                    # option is from section_defaults:
                    # it is removed in order to be replaced by eventually new value
                    option.defined = False
    return section_defaults


class SchemaSection(Section):
    """A section class to perform validation. All values must be Validator
       instances.

       The 'unexpected_option_validator' is used to validate unexpected
       options (options found in the section to be validated, but not
       in the schema). By default it is 'Complain()', which
       raises an UnexpectedOptionError. The 'Ignore()' validator
       can be used to ignore unexpected options (they will be kept in
       the validated section), while the 'Remove()' validator can be used
       to remove unexpected options from the validated section.


       Parameters
       ----------
       init: Mapping, optional
           some initial content
       dictionary: Mapping, optional
           the internal dictionary
       parent: zirkon.Section, optional
           the parent section
       name: str, optional
           the section name
       macros: bool, optional
           enables macros
       unexpected_option_validator: Validator, optional
           the zirkon.validator.Validator to be used for unexpected options
       use_defaults: bool, optional
           if True, adds default values to defaults
           (defaults to True)
    """
    SUPPORTED_LIST_TYPES = ()
    SUPPORTED_SCALAR_TYPES = (Validator, )

    def __init__(self, init=None, *, dictionary=None, parent=None, name=None,
                 macros=True, unexpected_option_validator=None, use_defaults=True):
        self._unexpected_option_validator = None
        self.unexpected_option_validator = unexpected_option_validator
        self._use_defaults = None
        self.use_defaults = use_defaults
        super().__init__(dictionary=dictionary, init=init, parent=parent,
                         macros=macros, name=name)

    @property
    def use_defaults(self):
        """Returns True if defaults are enabled.

        Returns
        -------
        bool
            True if defaults are enabled
        """
        return self._use_defaults

    @use_defaults.setter
    def use_defaults(self, value):
        """Enables/disables defaults.

        Parameters
        ----------
        value: bool
            if True, defaults are enabled
        """
        self._use_defaults = bool(value)

    @classmethod
    def _subsection_class(cls):
        return SchemaSection

    def _subsection(self, section_name, dictionary):
        return self._subsection_class()(dictionary=dictionary, name=section_name,
                                        macros=self.macros,
                                        unexpected_option_validator=self._unexpected_option_validator,
                                        use_defaults=self._use_defaults)

    @property
    def unexpected_option_validator(self):
        """Returns the validator to be used for unexpected options.

           Returns
           -------
           |Validator|
               the current validator for unexpected options
        """
        return self._unexpected_option_validator

    @unexpected_option_validator.setter
    def unexpected_option_validator(self, validator):
        """Sets the validator to be used for unexpected options.

           Parameters
           ----------
           validator: |Validator|
               the validator to be used for unexpected options

           Raises
           ------
           TypeError
               not a validator
        """
        if validator is None:
            validator = Complain()
        if not isinstance(validator, Validator):
            raise TypeError("{!r} is not a Validator".format(validator))
        self._unexpected_option_validator = validator

    def validate(self, section, *, validation=None, raise_on_error=False):
        """Validates 'section' and returns a ValidationSection with the found
           validation errors.

           Parameters
           ----------
           section: zirkon.Section
               the section to be validated
           validation: zirkon.Validation, optional
               the validation object to be used, or None
           raise_on_error: bool, optional
               if True, the first error is raised.

           Raises
           ------
           OptionValidationError
               option validation error

           Returns
           -------
           zirkon.Validation
               the validation result
        """
        if validation is None:
            validation = Validation()
        self.impl_validate(
            section=section,
            validation_section=validation,
            raise_on_error=raise_on_error)
        return validation

    def impl_validate(self, section, validation_section, *, raise_on_error=False, parent_fqname=''):
        """Implementation of the validate method.

           Parameters
           ----------
           section: zirkon.Section
               the section to be validated
           validation_section: zirkon.validation_section.ValidationSection, optional
               the ValidationSection object to be used, or None
           raise_on_error: bool, optional
               if True, the first error is raised.
           parent_fqname: str, optional
               the fully qualified name (with dots) of the parent

           Raises
           ------
           zirkon.validator.OptionValidationError
               option validation error
        """
        args = dict(raise_on_error=raise_on_error, parent_fqname=parent_fqname)
        self.impl_validate_options(section=section, validation_section=validation_section, **args)
        self.impl_validate_subsections(section=section, validation_section=validation_section, **args)

    def impl_validate_subsections(self, *, section, validation_section, raise_on_error=False, parent_fqname=''):
        """Implementation of the validate method for subsections

           Parameters
           ----------
           section: zirkon.Section
               the section to be validated
           validation_section: zirkon.validation_section.ValidationSection, optional
               the ValidationSection object to be used, or None
           raise_on_error: bool, optional
               if True, the first error is raised.
           parent_fqname: str, optional
               the fully qualified name (with dots) of the parent

           Raises
           ------
           zirkon.validator.OptionValidationError
               option validation error
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
                    unexpected_option_validator=self._unexpected_option_validator)
                sub_validation_section = ValidationSection()
                schema_subsection.impl_validate(
                    section[subsection_name],
                    validation_section=sub_validation_section,
                    raise_on_error=raise_on_error,
                    parent_fqname=subsection_fqname)
                if sub_validation_section:
                    validation_section[subsection_name] = sub_validation_section

    def impl_validate_options(self, *, section, validation_section, raise_on_error=False, parent_fqname=''):
        """Implementation of the validate method for options

           Parameters
           ----------
           section: zirkon.Section
               the section to be validated
           validation_section: zirkon.validation_section.ValidationSection, optional
               the ValidationSection object to be used, or None
           raise_on_error: bool, optional
               if True, the first error is raised.
           parent_fqname: str, optional
               the fully qualified name (with dots) of the parent

           Raises
           ------
           zirkon.validator.OptionValidationError
               option validation error
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
                self._validate_option(
                    validator=validator,
                    section=section,
                    validation_section=validation_section,
                    option_name=option_name,
                    option=option,
                    raise_on_error=raise_on_error)
        # unexpected options:
        for option_name, option_value in list(section.options()):
            if option_name not in expected_option_names:
                validator = self._unexpected_option_validator
                fqname = parent_fqname + option_name
                option = Option(name=fqname, value=option_value, defined=True)
                self._validate_option(
                    validator=validator,
                    validation_section=validation_section,
                    section=section,
                    option_name=option_name,
                    option=option,
                    raise_on_error=raise_on_error)

    def _validate_option(self, *, validator, section, validation_section,
                         option_name, raise_on_error, option):
        """Validates an option and uses the validation result to
           eventually change the option value.
           Used to implement SchemaSection.impl_validate(...) method.
        """
        section_defaults = _reset_option_default(section=section, option=option, option_name=option_name)
        prev_defined = option.defined
        prev_value = option.value
        try:
            validator.validate_option(option, section)
        except OptionValidationError as err:
            validation_section[option_name] = err
            if raise_on_error:
                raise
        else:
            if not option.defined:
                if prev_defined:
                    del section[option_name]
            else:
                if option.value is not prev_value:
                    if prev_defined or not self._use_defaults:
                        section[option_name] = option.value
                    else:
                        section_defaults[option_name] = option.value


