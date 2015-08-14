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
Validator classes
"""

__author__ = "Simone Campagna"

__all__ = [
    'Validator',
    'Int',
    'IntList',
    'IntTuple',
    'IntChoice',
    'Float',
    'FloatList',
    'FloatTuple',
    'FloatChoice',
    'Str',
    'StrList',
    'StrTuple',
    'StrChoice',
    'Bool',
    'BoolList',
    'BoolTuple',
    'BoolChoice',
    'ValidatorInstance',
    'Ignore',
    'Remove',
    'Complain',
]

from ..toolbox import serializer
from ..deferred_object import ROOT, SECTION

from .validator import Validator

from .int_validators import Int, \
    IntList, IntTuple, IntChoice

from .float_validators import Float, \
    FloatList, FloatTuple, FloatChoice

from .str_validators import Str, \
    StrList, StrTuple, StrChoice

from .bool_validators import Bool, \
    BoolList, BoolTuple, BoolChoice

from .validator_instance import ValidatorInstance
from .complain import Complain
from .ignore import Ignore
from .remove import Remove

from ..toolbox.unrepr import unrepr
from ..toolbox.subclass import find_subclass

from .error import OptionValidationError
from .option import Option


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

        def _ov_error_text_encode(option_validation_error):
            """_ov_error_text_encode(validator)
               OptionValidationError encoder.
            """
            return "{}({!r})".format(
                type(option_validation_error).__name__,
                str(option_validation_error))

        def _ov_error_text_decode(type_name, repr_data):
            """_ov_error_text_encode(type_name, repr_data)
               OptionValidationError decoder.
            """
            globals_d = {Option.__name__: Option}
            option_validation_error_class = find_subclass(OptionValidationError, type_name, include_self=False)
            if option_validation_error_class is None:
                raise NameError("undefined OptionValidationError class {}".format(type_name))
            globals_d[type_name] = option_validation_error_class
            globals_d['ROOT'] = ROOT
            globals_d['SECTION'] = SECTION
            return unrepr(repr_data, globals_d)

        _text_serializer_module.TextSerializer.codec_catalog().add_codec(
            class_=OptionValidationError,
            encode=_ov_error_text_encode,
            decode=_ov_error_text_decode,
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

        def _option_json_encode(option):
            """_option_json_encode(validator)
               Option JSON encoder.
            """
            return {'name': option.name,
                    'value': option.value,
                    'defined': option.defined}

        def _option_json_decode(type_name, args):
            """_option_json_encode(type_name, repr_data)
               OptionValalue JSON decoder.
            """
            option_class = find_subclass(Option, type_name, include_self=True)
            if option_class is None:
                raise NameError("undefined Option class {}".format(type_name))
            return option_class(**args)

        _json_serializer_module.JSONSerializer.codec_catalog().add_codec(
            class_=Option,
            encode=_option_json_encode,
            decode=_option_json_decode,
        )

        def _ov_error_json_encode(option_validation_error):
            """_ov_error_json_encode(validator)
               OptionValidationError JSON encoder.
            """
            return {'exception_args': option_validation_error.args}

        def _ov_error_json_decode(type_name, args):
            """_ov_error_json_encode(type_name, repr_data)
               OptionValidationError JSON decoder.
            """
            ov_error_subclass = find_subclass(OptionValidationError, type_name)
            if ov_error_subclass is None:
                raise NameError("undefined OptionValidationError subclass {}".format(type_name))
            return ov_error_subclass(*args['exception_args'])

        _json_serializer_module.JSONSerializer.codec_catalog().add_codec(
            class_=OptionValidationError,
            encode=_ov_error_json_encode,
            decode=_ov_error_json_decode,
        )

_setup_codecs()
