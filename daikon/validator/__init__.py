# -*- coding: utf-8 -*-
"""
config.validator
================
Parameter validator classes
"""

__all__ = [
    'ValidatorBase',
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
    'Validator',
    'Ignore',
    'Remove',
    'UnexpectedParameter',
]

import collections

from ..serializer import json_serializer
from ..serializer import configobj_serializer

from .validator_base import ValidatorBase

from .int_validators import Int, \
    IntList, IntTuple, IntOption

from .float_validators import Float, \
    FloatList, FloatTuple, FloatOption

from .str_validators import Str, \
    StrList, StrTuple, StrOption

from .bool_validators import Bool, \
    BoolList, BoolTuple, BoolOption

from .validator import Validator
from .unexpected_parameter import UnexpectedParameter
from .ignore import Ignore
from .remove import Remove

json_serializer.add_coder(
    class_=ValidatorBase,
    encode=(lambda obj: collections.OrderedDict([('__validator_repr__', obj.validator_repr())])),
    decode=(lambda dct: ValidatorBase.validator_unrepr(dct['__validator_repr__'])),
)

configobj_serializer.update_globals(ValidatorBase.subclasses_dict())

