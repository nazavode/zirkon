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
Implementation of the ConfigBase mixin class, adding serialization methods.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'ConfigBase',
    'ConfigValidationError',
]


from .section import Section
from .toolbox.serializer import Serializer
from .toolbox.unrepr import unrepr
from .macros import ROOT, SECTION


class ConfigValidationError(Exception):
    """This exception class represents a validation error; the 'validation' attribute
       contains the Validation result.
    """
    def __init__(self, validation, message=None):
        if message is None:
            message = "validation error: {}".format(validation)
        super().__init__(message)
        self.validation = validation


class ConfigBase(Section):
    r""" Config base class; adds to Section serialization/deserialization methods.

         Parameters
         ----------
         init: |Mapping|, optional
             some initialization content
         dictionary: |Mapping|, optional
             the internal dictionary
         schema: |Schema|, optional
             the validation schema
         validate: bool, optional
             self validate during initialization;
         macros: bool, optional
             enables macros (defaults to True);
         \*\*section_options:
             keyword arguments to be passed to the Section contructor
    """

    def __init__(self, init=None, *, dictionary=None, schema=None, validate=True,
                 macros=True, **section_options):
        super().__init__(dictionary=dictionary, init=init,
                         macros=macros, **section_options)
        self._schema = None
        self.set_schema(schema=schema, validate=validate)

    @property
    def schema(self):
        """Gets the schema attribute"""
        return self._schema

    @schema.setter
    def schema(self, schema):
        """Sets the schema attribute"""
        return self.set_schema(schema)

    def set_schema(self, schema, *, validate=True):
        """Sets the validation schema

           Parameters
           ----------
           schema: |Schema|
               the schema to be used for self-validation
               (can be None to disable self-validation)
           validate: bool
               execute self-validation now (defaults to True)

           Raises
           ------
           |OptionValidationError|
               option validation error
        """
        self._schema = schema
        if validate:
            self.self_validate(raise_on_error=True)

    def self_validate(self, raise_on_error=False):
        """Validate the config itself using the 'schema' attribute.

           Parameters
           ----------
           raise_on_error: bool, optional
               raise an exception at the very first validation error; defaults to False;

           Raises
           ------
           |OptionValidationError|
               option validation error

           Returns
           -------
           |Validation|
               the validation object containing all the found errors.
               If 'raise_on_errors' is True, it contains at most one error.
        """
        if self._schema is not None:
            validation = self._schema.validate(self, raise_on_error=False)
            if raise_on_error and validation:
                raise ConfigValidationError(validation=validation)
            else:
                return validation

    @classmethod
    def get_serializer(cls, protocol):
        """Returns a serializer for the required protocol.

           Parameters
           ----------
           protocol: str
               a valid protocol name

           Raises
           ------
           ValueError
               unsupported serialization protocol

           Returns
           -------
           zirkon.toolbox.serializer.Serializer
               the serializer instance.
        """
        serializer_class = Serializer.get_class(protocol)
        if serializer_class is None:
            raise ValueError("serialization protocol {} not available [{}]".format(
                protocol,
                '|'.join(registered_class.class_tag() for registered_class in Serializer.classes()),
            ))
        return serializer_class()

    def to_string(self, protocol, *, defaults=False):
        """Serializes to string according to 'protocol'.

           Parameters
           ----------
           protocol: str
               a valid protocol name
           defaults: bool, optional
               if True, serialize also default values (defaults to False)

           Raises
           ------
           |OptionValidationError|
               option validation error

           Returns
           -------
           str
               the serialization string
        """
        self.self_validate(raise_on_error=True)
        serializer_instance = self.get_serializer(protocol)
        obj = self.as_dict(defaults=defaults, evaluate=False)
        return serializer_instance.to_string(obj)

    def to_stream(self, stream, protocol, *, defaults=False):
        """Serializes to file stream 'stream' according to 'protocol'.

           Parameters
           ----------
           stream: file
               a file stream
           protocol: str
               a valid protocol name
           defaults: bool, optional
               if True, serialize also default values (defaults to False)

           Raises
           ------
           |OptionValidationError|
               option validation error

        """
        self.self_validate(raise_on_error=True)
        serializer_instance = self.get_serializer(protocol)
        obj = self.as_dict(defaults=defaults, evaluate=False)
        serializer_instance.to_stream(obj, stream)

    def to_file(self, filename, protocol, *, defaults=False):
        """Serializes to file 'filename' according to 'protocol'.

           Parameters
           ----------
           filename: str
               a file name
           protocol: str
               a valid protocol name
           defaults: bool, optional
               if True, serialize also default values (defaults to False)

           Raises
           ------
           |OptionValidationError|
               option validation error

        """
        self.self_validate(raise_on_error=True)
        serializer_instance = self.get_serializer(protocol)
        obj = self.as_dict(defaults=defaults, evaluate=False)
        serializer_instance.to_file(obj, filename)

    def dump(self, stream=None, protocol="zirkon", *, defaults=False):
        self.self_validate(raise_on_error=True)
        super().dump(stream=stream, protocol=protocol, defaults=defaults)

    @classmethod
    def from_file(cls, filename, protocol, *,
                  dictionary=None, schema=None, validate=True, **config_args):
        r"""Deserializes from file 'filename' according to 'protocol'.

             Parameters
             ----------
             filename: str
                 a file name
             protocol: str
                 a valid protocol name
             dictionary: mapping, optional
                 the internal dictionary (defaults to None)
             schema: Schema, optional
                 the validation schema (defaults to None)
             validate: bool, optional
                 if True self-validate on contruction (defaults to True)
             \*\*config_args
                 keyword arguments to be passed to the constructor

             Returns
             -------
             cls
                 the deserialized object
        """
        serializer_instance = cls.get_serializer(protocol)
        content = serializer_instance.from_file(filename)
        instance = cls(init=content, dictionary=dictionary, **config_args)
        instance.set_schema(schema=schema, validate=validate)
        return instance

    @classmethod
    def from_stream(cls, stream, protocol, *,
                    dictionary=None, filename=None,
                    schema=None, validate=True, **config_args):
        r"""Deserializes from file stream 'stream' according to 'protocol'.

            Parameters
            ----------
            stream: file
                a file stream
            protocol: str
                a valid protocol name
            dictionary: mapping, optional
                the internal dictionary (defaults to None)
            schema: Schema, optional
                the validation schema (defaults to None)
            validate: bool, optional
                if True self-validate on contruction (defaults to True)
            \*\*config_args
                keyword arguments to be passed to the constructor

            Returns
            -------
            cls
                the deserialized object
        """
        serializer_instance = cls.get_serializer(protocol)
        content = serializer_instance.from_stream(stream, filename=filename)
        instance = cls(init=content, dictionary=dictionary, **config_args)
        instance.set_schema(schema=schema, validate=validate)
        return instance

    @classmethod
    def from_string(cls, string, protocol, *,
                    dictionary=None, filename=None, schema=None, validate=True, **config_args):
        r"""Deserializes from string 'string' according to 'protocol'.

            Parameters
            ----------
            string: str
                a serialization string
            protocol: str
                a valid protocol name
            dictionary: mapping, optional
                the internal dictionary (defaults to None)
            schema: Schema, optional
                the validation schema (defaults to None)
            validate: bool, optional
                if True self-validate on contruction (defaults to True)
            \*\*config_args
                keyword arguments to be passed to the constructor

            Returns
            -------
            cls
                the deserialized object
        """
        serializer_instance = cls.get_serializer(protocol)
        content = serializer_instance.from_string(string, filename=filename)
        instance = cls(init=content, dictionary=dictionary, **config_args)
        instance.set_schema(schema=schema, validate=validate)
        return instance

    def read(self, filename, protocol):
        """Reads from file 'filename' according to 'protocol'. The initial content is cleared.

           Parameters
           ----------
           filename: str
               a file name
           protocol: str
               a valid protocol name

           Raises
           ------
           |OptionValidationError|
               option validation error
        """
        self.clear()
        serializer_instance = self.get_serializer(protocol)
        content = serializer_instance.from_file(filename)
        self.update(content)
        self.self_validate(raise_on_error=True)

    def write(self, filename, protocol):
        """Writes to file 'filename' according to 'protocol'.

           Parameters
           ----------
           filename: str
               a file name
           protocol: str
               a valid protocol name

           Raises
           ------
           |OptionValidationError|
               option validation error
        """
        self.to_file(filename, protocol)


from .toolbox import serializer
from .toolbox.macro import Macro
from .toolbox.subclass import find_subclass


# macro codecs:
def _setup_codecs():
    """_setup_codecs()
       Setup codecs for validators.
    """
    _json_serializer_module = getattr(serializer, 'json_serializer', None)
    if _json_serializer_module is not None:
        def _macro_encode(macro_object):
            """Encodes a Macro object to json.

               Parameters
               ----------
               macro_object: Macro
                   the macro object

               Returns
               -------
               dict
                   the encoded dictionary
            """
            return {'macro_expression': macro_object.unparse()}

        def _macro_decode(macro_class_name, arguments):
            """Decodes a Macro object from JSON.

               Parameters
               ----------
               macro_class_name: str
                   the macro class name
               arguments: dict
                   the encoded dict

               Raises
               ------
               NameError
                   class not found

               Returns
               -------
               Macro
                   the decoded object
            """
            macro_class = find_subclass(Macro, macro_class_name, include_self=True)
            if macro_class is None:
                raise NameError("undefined Macro class {}".format(macro_class_name))
            return eval(arguments['macro_expression'], {'ROOT': ROOT, 'SECTION': SECTION})  # pylint: disable=eval-used

        _json_serializer_module.JSONSerializer.codec_catalog().add_codec(
            class_type=Macro,
            encode=_macro_encode,
            decode=_macro_decode,
        )

    _text_serializer_module = getattr(serializer, 'text_serializer', None)
    if _text_serializer_module is not None:
        def _str_text_encode(str_object):
            """Encodes a string to configobj/zirkon.

               Parameters
               ----------
               str_object: str
                   the string

               Returns
               -------
               str
                   the encoded string
            """
            return repr(str_object)

        def _str_text_decode(type_name, repr_data):  # pylint: disable=unused-argument
            """Decodes a string from configobj/zirkon.

               Parameters
               ----------
               type_name: str
                   the class name ("str")
               repr_data: str
                   the encoded string

               Returns
               -------
               str: the decoded string
            """
            return unrepr(repr_data, {'SECTION': SECTION, 'ROOT': ROOT})

        _text_serializer_module.TextSerializer.codec_catalog().add_codec(
            class_type=str,
            encode=_str_text_encode,
            decode=_str_text_decode,
        )

_setup_codecs()

