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
Validator classes.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'

__all__ = [
    # validators:
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
    # errors:
    'OptionValidationError', 'InvalidContentError', 'MissingRequiredOptionError',
    'UnexpectedSectionError', 'UnexpectedOptionError', 'InvalidTypeError',
    'InvalidValueError', 'MinValueError', 'MaxValueError', 'InvalidChoiceError',
    'InvalidLengthError', 'MinLengthError', 'MaxLengthError',
]

from ..toolbox import serializer
from ..macros import ROOT, SECTION

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

from .error import \
    OptionValidationError, \
    InvalidContentError, \
    MissingRequiredOptionError, \
    UnexpectedSectionError, \
    UnexpectedOptionError, \
    InvalidTypeError, \
    InvalidValueError, \
    MinValueError, \
    MaxValueError, \
    InvalidChoiceError, \
    InvalidLengthError, \
    MinLengthError, \
    MaxLengthError


# Validator codecs:
def _setup_codecs():
    """_setup_codecs()
       Setup codecs for validators.
    """
    _text_serializer_module = getattr(serializer, 'text_serializer', None)
    if _text_serializer_module is not None:
        def _validator_text_encode(validator):
            """Encodes validator for configobj/zirkon serializers.

               Parameters
               ----------
               validator: Validator
                   the validator to be encoded

               Returns
               -------
               str
                   the validator's representation
            """
            return repr(validator)

        def _validator_text_decode(type_name, repr_data):  # pylint: disable=unused-argument
            """Decodes validator from configobj/zirkon serializers.
               configobj/zirkon decoder for Validator instances

               Parameters
               ----------
               type_name: str
                   the type name
               repr_data: str
                   the validator's representation

               Returns
               -------
               Validator
                   the validator
            """
            globals_d = {}
            globals_d['ROOT'] = ROOT
            globals_d['SECTION'] = SECTION
            globals_d[type_name] = Validator.class_dict()[type_name]
            return unrepr(repr_data, globals_d)

        _text_serializer_module.TextSerializer.codec_catalog().add_codec(
            class_type=Validator,
            encode=_validator_text_encode,
            decode=_validator_text_decode,
        )

        def _ov_error_text_encode(option_validation_error):
            """Encodes OptionValidationError for configobj/zirkon serializers.

               Parameters
               ----------
               option_validation_error: OptionValidationError
                   the error

               Returns
               -------
               str
                   the errors's representation
            """
            return "{}({!r})".format(
                type(option_validation_error).__name__,
                str(option_validation_error))

        def _ov_error_text_decode(type_name, repr_data):
            """Decodes OptionValidationError from configobj/zirkon serializers.

               Parameters
               ----------
               type_name: str
                   the type name
               repr_data: str
                   the errors's representation

               Raises
               ------
               NameError
                   class not found

               Returns
               -------
               OptionValidationError
                   the error
            """
            globals_d = {}
            option_validation_error_class = find_subclass(OptionValidationError, type_name, include_self=False)
            if option_validation_error_class is None:  # pragma: no cover
                raise NameError("undefined OptionValidationError class {}".format(type_name))
            globals_d[type_name] = option_validation_error_class
            globals_d['ROOT'] = ROOT
            globals_d['SECTION'] = SECTION
            return unrepr(repr_data, globals_d)

        _text_serializer_module.TextSerializer.codec_catalog().add_codec(
            class_type=OptionValidationError,
            encode=_ov_error_text_encode,
            decode=_ov_error_text_decode,
        )

    _json_serializer_module = getattr(serializer, 'json_serializer', None)
    if _json_serializer_module is not None:
        def _validator_json_encode(validator):
            """Encodes validators for json serializer.

               Parameters
               ----------
               validator: Validator
                   the validator to be encoded

               Returns
               -------
               str
                   the validators's representation
            """
            return validator.actual_arguments.copy()

        def _validator_json_decode(validator_name, arguments):
            """Decodes OptionValidationError from configobj/zirkon serializers.

               Parameters
               ----------
               validator_name: str
                   the validator's name
               arguments: str
                   the validator's arguments

               Returns
               -------
               Validator
                   the error
            """
            validator_class = Validator.get_class(validator_name)
            return validator_class(**arguments)

        _json_serializer_module.JSONSerializer.codec_catalog().add_codec(
            class_type=Validator,
            encode=_validator_json_encode,
            decode=_validator_json_decode,
        )

        def _ov_error_json_encode(option_validation_error):
            """Encodes OptionValidationErrors for json serializer.

               Parameters
               ----------
               option_validation_error: OptionValidationError
                   the error to be encoded

               Returns
               -------
               str
                   the errors's representation
            """
            return {'exception_args': option_validation_error.args}

        def _ov_error_json_decode(type_name, args):
            """Decodes OptionValidationError from configobj/zirkon serializers.

               Parameters
               ----------
               type_name: str
                   the type name
               args: tuple
                   the errors's args

               Raises
               ------
               NameError
                   class not found


               Returns
               -------
               OptionValidationError
                   the error
            """
            ov_error_subclass = find_subclass(OptionValidationError, type_name)
            if ov_error_subclass is None:  # pragma: no cover
                raise NameError("undefined OptionValidationError subclass {}".format(type_name))
            return ov_error_subclass(*args['exception_args'])

        _json_serializer_module.JSONSerializer.codec_catalog().add_codec(
            class_type=OptionValidationError,
            encode=_ov_error_json_encode,
            decode=_ov_error_json_decode,
        )

_setup_codecs()
