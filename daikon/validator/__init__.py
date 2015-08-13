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

from ..toolbox import serializer
from ..deferred_object import ROOT, SECTION

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
from ..toolbox.subclass import find_subclass

from .error import KeyValidationError
from .key_value import KeyValue


# Validator codecs:
def _setup_codecs():
    """_setup_codecs()
       Setup codecs for validators.
    """
    _text_serializer_module = getattr(serializer, 'text_serializer', None)
    if _text_serializer_module is not None:
        def _validator_text_encode(validator):
            """_validator_text_encode(validator)
               ConfigObj/Daikon encoder for Validator instances
            """
            return repr(validator)

        def _validator_text_decode(type_name, repr_data):  # pylint: disable=W0613
            """_validator_text_decode(validator_name, arguments)
               ConfigObj/Daikon decoder for Validator instances
            """
            globals_d = {}
            globals_d['ROOT'] = ROOT
            globals_d['SECTION'] = SECTION
            globals_d[type_name] = Validator.class_dict()[type_name]
            return unrepr(repr_data, globals_d)

        _text_serializer_module.TextSerializer.codec_catalog().add_codec(
            class_=Validator,
            encode=_validator_text_encode,
            decode=_validator_text_decode,
        )

        def _kv_error_text_encode(key_validation_error):
            """_kv_error_text_encode(validator)
               KeyValidationError encoder.
            """
            return "{}({!r}, {!r})".format(
                type(key_validation_error).__name__,
                key_validation_error.key_value,
                key_validation_error.message)

        def _kv_error_text_decode(type_name, repr_data):
            """_kv_error_text_encode(type_name, repr_data)
               KeyValidationError decoder.
            """
            globals_d = {KeyValue.__name__: KeyValue}
            key_validation_error_class = find_subclass(KeyValidationError, type_name, include_self=False)
            if key_validation_error_class is None:
                raise NameError("undefined KeyValidationError class {}".format(type_name))
            globals_d[type_name] = key_validation_error_class
            globals_d['ROOT'] = ROOT
            globals_d['SECTION'] = SECTION
            return unrepr(repr_data, globals_d)

        _text_serializer_module.TextSerializer.codec_catalog().add_codec(
            class_=KeyValidationError,
            encode=_kv_error_text_encode,
            decode=_kv_error_text_decode,
        )

    _json_serializer_module = getattr(serializer, 'json_serializer', None)
    if _json_serializer_module is not None:
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
            return validator_class(**arguments)

        _json_serializer_module.JSONSerializer.codec_catalog().add_codec(
            class_=Validator,
            encode=_validator_json_encode,
            decode=_validator_json_decode,
        )

        def _key_value_json_encode(key_value):
            """_key_value_json_encode(validator)
               KeyValue JSON encoder.
            """
            return {'key': key_value.key,
                    'value': key_value.value,
                    'defined': key_value.defined}

        def _key_value_json_decode(type_name, args):
            """_key_value_json_encode(type_name, repr_data)
               KeyValalue JSON decoder.
            """
            key_value_class = find_subclass(KeyValue, type_name, include_self=True)
            if key_value_class is None:
                raise NameError("undefined KeyValue class {}".format(type_name))
            return key_value_class(**args)

        _json_serializer_module.JSONSerializer.codec_catalog().add_codec(
            class_=KeyValue,
            encode=_key_value_json_encode,
            decode=_key_value_json_decode,
        )

        def _kv_error_json_encode(key_validation_error):
            """_kv_error_json_encode(validator)
               KeyValidationError JSON encoder.
            """
            return {'key_value': key_validation_error.key_value,
                    'message': key_validation_error.message}

        def _kv_error_json_decode(type_name, args):
            """_kv_error_json_encode(type_name, repr_data)
               KeyValidationError JSON decoder.
            """
            key_validation_error_subclass = find_subclass(KeyValidationError, type_name)
            if key_validation_error_subclass is None:
                raise NameError("undefined KeyValidationError subclass {}".format(type_name))
            return key_validation_error_subclass(**args)

        _json_serializer_module.JSONSerializer.codec_catalog().add_codec(
            class_=KeyValidationError,
            encode=_kv_error_json_encode,
            decode=_kv_error_json_decode,
        )
_setup_codecs()
