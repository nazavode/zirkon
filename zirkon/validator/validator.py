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
Implementation of the Validator base class.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'Validator',
]

from ..toolbox.registry import Registry
from ..toolbox.compose import Composer, ArgumentStore
from .option import Option


class Validator(Registry):
    r"""Base class for validators.

        Parameters
        ----------
        argument_store: ArgumentStore, optional
            the argument store
        \*\*arguments: dict
            the actual arguments
    """
    CHECK_COMPOSER = None

    def __init__(self, *, argument_store=None, **arguments):
        if argument_store is None:
            argument_store = ArgumentStore()
        argument_store.update(arguments)
        self.argument_store = argument_store

        self.actual_arguments, self.checks = self.bind_arguments(self.argument_store, prefix='')

        Composer.verify_argument_store(self.argument_store)

        # check auto-validation:
        for check in self.checks:
            check.self_validate(validator=self)

    def bind_arguments(self, argument_store, prefix=''):
        """Binds actual arguments to the CHECK_COMPOSER instance.

           Parameters
           ----------
           argument_store: ArgumentStore, optional
               the argument store
           prefix: str, optional
               an argument prefix; defaults to ''

           Returns
           -------
           tuple
               a 2-tuple containing (actual_arguments, check_composer)
        """
        return self.CHECK_COMPOSER.partial(argument_store, prefix=prefix)

    def __repr__(self):
        args = ', '.join("{}={!r}".format(o_name, o_value) for o_name, o_value in self.argument_store.items())
        return "{}({})".format(self.__class__.__name__, args)

    def validate(self, name, value, defined, section=None):
        """Validates a name/value/defined triplet.

           Parameters
           ----------
           name: str
               the option name
           value: |any|
               the option value
           defined: bool
               True if option is defined in config
           section: |Section|, optional
               the containing section

           Returns
           -------
           bool
               True if validation is successful
        """
        option = Option(name=name, defined=defined, value=value)
        return self.validate_option(option, section=section)

    def validate_option(self, option, section=None):
        """Validates a Option object.

           Parameters
           ----------
           option: |Option|
               the option to be validated

           Returns
           -------
           bool
               True if validation is successful
        """
        for check in self.checks:
            check.check(option, section)
        return option.value

    def __eq__(self, validator):
        if self.__class__ != validator.__class__:
            return False
        return self.argument_store == validator.argument_store
