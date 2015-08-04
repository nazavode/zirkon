# -*- coding: utf-8 -*-
"""
config.validator
================
Parameter validator classes
"""

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

json_serializer.add_coder(
    class_=Validator,
    encode=(lambda obj: collections.OrderedDict([('__repr__', obj.repr())])),
    decode=(lambda dct: Validator.unrepr(dct['__repr__'])),
)

configobj_serializer.update_globals(Validator.subclasses_dict())

