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
config.validator
================
Parameter validator classes
"""

__author__ = "Simone Campagna"

__all__ = [
    'Validator',
    'Int',
    'IntList',
    'IntTuple',
    'IntOption',
    'Float',
    'FloatList',
    'FloatTuple',
    'FloatOption',
    'Str',
    'StrList',
    'StrTuple',
    'StrOption',
    'Bool',
    'BoolList',
    'BoolTuple',
    'BoolOption',
    'ValidatorInstance',
    'Ignore',
    'Remove',
    'UnexpectedParameter',
]

import collections

from ..toolbox.serializer import json_serializer
from ..toolbox.serializer import text_serializer

from .validator import Validator

from .int_validators import Int, \
    IntList, IntTuple, IntOption

from .float_validators import Float, \
    FloatList, FloatTuple, FloatOption

from .str_validators import Str, \
    StrList, StrTuple, StrOption

from .bool_validators import Bool, \
    BoolList, BoolTuple, BoolOption

from .validator_instance import ValidatorInstance
from .unexpected_parameter import UnexpectedParameter
from .ignore import Ignore
from .remove import Remove

from ..toolbox.unrepr import unrepr

def _validator_json_encode(validator):
    """_validator_json_encode(validator)
       JSON encoder for Validator instances
    """
    return validator.actual_arguments.copy()

def _validator_json_decode(validator_name, arguments):
    """_validator_json_decode(validator_name, arguments)
       JSON decoder for Validator instances
    """
    validator_class = Validator.get_class(validator_name)
    #print("::: (((", validator_name, validator_class, arguments)
    return validator_class(**arguments)

json_serializer.JSONSerializer.codec_catalog().add_codec(
    class_=Validator,
    encode=_validator_json_encode,
    decode=_validator_json_decode,
)

def _validator_text_encode(validator):
    """_validator_text_encode(validator)
       ConfigObj/Daikon encoder for Validator instances
    """
    return repr(validator)

def _validator_text_decode(type_name, repr_data):  # pylint: disable=W0613
    """_validator_text_decode(validator_name, arguments)
       ConfigObj/Daikon decoder for Validator instances
    """
    return unrepr(repr_data, Validator.class_dict())

text_serializer.TextSerializer.codec_catalog().add_codec(
    class_=Validator,
    encode=_validator_text_encode,
    decode=_validator_text_decode,
)


