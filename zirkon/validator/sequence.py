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
Implementation of the Sequence validator class.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'Sequence',
]

from .option import Option
from .validator import Validator


class Sequence(Validator):
    """Base class for sequence (list, tuple) validators."""
    ITEM_VALIDATOR_CLASS = type(None)

    def bind_arguments(self, argument_store, prefix=''):
        sub_prefix = prefix + 'item_'
        sub_argument_store = argument_store.split(prefix=sub_prefix)
        self.item_validator = self.ITEM_VALIDATOR_CLASS(argument_store=sub_argument_store)
        argument_store.merge(sub_argument_store, prefix=sub_prefix)
        actual_arguments, objects = super().bind_arguments(argument_store, prefix=prefix)
        for argument_name, argument_value in self.item_validator.actual_arguments.items():
            actual_arguments[sub_prefix + argument_name] = argument_value
        return actual_arguments, objects

    def validate_option(self, option, section=None):
        super().validate_option(option, section)
        if option.defined and option.value:
            validated_item_values = []
            changed = False
            for item_idx, item_value in enumerate(option.value):
                item_name = "{}[{}]".format(option.name, item_idx)
                item_option = Option(name=item_name, value=item_value, defined=True)
                validated_item_value = self.item_validator.validate_option(item_option)
                validated_item_values.append(validated_item_value)
                if item_value is not validated_item_value:
                    changed = True
            if changed:
                sequence_type = type(option.value)
                option.value = sequence_type(validated_item_values)
        return option.value
