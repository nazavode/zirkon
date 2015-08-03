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
config.validator.sequence_validator
===================================
Implementation of the SequenceValidator class
"""

__author__ = "Simone Campagna"
__all__ = [
    'SequenceValidator',
]

from .key_value import KeyValue
from .validator import Validator


class SequenceValidator(Validator):
    """SequenceValidator(...)
       Base class for sequence (list, tuple) validators.
    """

    ITEM_VALIDATOR_CLASS = None
    def bind_arguments(self, argument_store, prefix=''):
        sub_prefix = prefix + 'item_'
        sub_argument_store = argument_store.split(prefix=sub_prefix)
        self.item_validator = self.ITEM_VALIDATOR_CLASS(argument_store=sub_argument_store)
        argument_store.merge(sub_argument_store, prefix=sub_prefix)
        return super().bind_arguments(argument_store, prefix=prefix)

    def validate_key_value(self, key_value, mode=None):
        super().validate_key_value(key_value, mode=mode)
        if key_value.defined and key_value.value:
            validated_item_values = []
            changed = False
            for item_idx, item_value in enumerate(key_value.value):
                item_key = "{}[{}]".format(key_value.key, item_idx)
                item_key_value = KeyValue(key=item_key, value=item_value, defined=True)
                validated_item_value = self.item_validator.validate_key_value(item_key_value, mode=mode)
                validated_item_values.append(validated_item_value)
                if item_value != validated_item_value:
                    changed = True
            if changed:
                sequence_type = type(key_value.value)
                key_value.value = sequence_type(validated_item_values)
        return key_value.value
