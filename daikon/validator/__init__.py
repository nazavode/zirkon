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

from ..serializer import json_serializer
from ..serializer import configobj_serializer

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

json_serializer.JSONSerializer.codec_registry().add_codec(
    class_=Validator,
    encode=(lambda obj: collections.OrderedDict([('__repr__', obj.repr())])),
    decode=(lambda dct: Validator.unrepr(dct['__repr__'])),
)

configobj_serializer.update_globals(Validator.subclasses_dict())

