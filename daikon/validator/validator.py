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
Implementation of the Validator class
"""

__author__ = "Simone Campagna"
__all__ = [
    'Validator',
]

from ..utils.plugin import Plugin
from .key_value import KeyValue
from .option_store import OptionStore

class Validator(Plugin):
    CHECK_CLASSES = ()
    def __init__(self, *, option_store=None, **options):
        if option_store is None:
            option_store = OptionStore()
        option_store.update(options)
        self.checks = []
        for check_class in self.CHECK_CLASSES:
            check = check_class.build(option_store)
            self.checks.append(check)
        invalid_options = list(option_store.invalid())
        if invalid_options:
            raise TypeError("{}: invalid options {}".format(
                self.__class__.__name__,
                ', '.join(invalid_options),
            ))
        self.option_store = option_store
        # check auto-validation:
        for check in self.checks:
            check.auto_validate(validator=self)

    def __repr__(self):
        args = ', '.join("{}={!r}".format(o_name, o_value) for o_name, o_value in self.option_store.items())
        return "{}({})".format(self.__class__.__name__, args)

    @classmethod
    def validator_unrepr(cls, vstring):
        return eval(vstring, cls.subclasses_dict())

    def validator_repr(self):
        args = ', '.join("{}={!r}".format(o_name, o_value) for o_name, o_value in self.option_store.items())
        return "{}({})".format(self.plugin_name(), args)

    @classmethod
    def plugin_name(cls):
        name = cls.__name__
        suffix = "Validator"
        if name.endswith(suffix):
            name = name[:-len(suffix)]
        return name

    def validate(self, key, defined, value):
        key_value = KeyValue(key=key, defined=defined, value=value)
        return self.validate_key_value(key_value)

    def validate_key_value(self, key_value):
        for check in self.checks:
            check.check(key_value)
        return key_value.value

    def __eq__(self, validator):
        print(type(self) == type(validator))
        print(self.option_store == validator.option_store)
        if self.__class__ != validator.__class__:
            return False
        return self.option_store == validator.option_store
        
     
