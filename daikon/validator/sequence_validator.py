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

import collections

from .key_value import KeyValue
from .option_store import OptionStore
from .validator import Validator


class SequenceValidator(Validator):
    ITEM_VALIDATOR_CLASS = None
    def __init__(self, *, option_store=None, **options):
        option_store = OptionStore(options)
        # sub options:
        item_prefix = "item_"
        sub_options = collections.OrderedDict()
        for option_name in options:
            if option_name.startswith(item_prefix):
                sub_option_name = option_name[len(item_prefix):]
                sub_options[sub_option_name] = option_store.get(option_name)
        sub_option_store = OptionStore(sub_options)
        self.item_validator = self.ITEM_VALIDATOR_CLASS(option_store=sub_option_store)
        super().__init__(option_store=option_store)
    

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
