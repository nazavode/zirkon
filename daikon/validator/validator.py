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
config.validator.validator
==========================
Implementation of the Validator base class
"""

__author__ = "Simone Campagna"
__all__ = [
    'Validator',
]

from ..toolbox.registry import Registry
from ..toolbox.compose import Composer, ArgumentStore
from .key_value import KeyValue


class Validator(Registry):
    """Validator(*, argument_store, **arguments)
       Base class for validators.
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
            check.auto_validate(validator=self)

    def bind_arguments(self, argument_store, prefix=''):
        """bind_arguments(argument_store, prefix='')
           Binds actual arguments to the CHECK_COMPOSER instance.
        """
        return self.CHECK_COMPOSER.partial(argument_store, prefix=prefix)

    def __repr__(self):
        args = ', '.join("{}={!r}".format(o_name, o_value) for o_name, o_value in self.argument_store.items())
        return "{}({})".format(self.__class__.__name__, args)

    def validate(self, key, value, defined):
        """validate(key, value, defined) -> validator repr
           Validate a key/value.
        """
        key_value = KeyValue(key=key, defined=defined, value=value)
        return self.validate_key_value(key_value)

    def validate_key_value(self, key_value):
        """validate(key, value, defined) -> validator repr
           Validate a KeyValue object.
        """
        for check in self.checks:
            check.do_check(key_value)
        return key_value.value

    def __eq__(self, validator):
        if self.__class__ != validator.__class__:
            return False
        return self.argument_store == validator.argument_store
