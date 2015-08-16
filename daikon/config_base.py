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
daikon.config.config_base
=========================
"""

__author__ = "Simone Campagna"
__all__ = [
    'ConfigBase',
    'ConfigValidationError',
]


from .section import Section
from .toolbox.serializer import Serializer
from .toolbox.unrepr import unrepr
from .deferred_object import ROOT, SECTION


class ConfigValidationError(Exception):
    """ConfigValidationError()
       Error in Config validation; the validation attribute contains the validation result.
    """
    def __init__(self, validation, message=None):
        if message is None:
            message = "validation error: {}".format(validation)
        super().__init__(message)
        self.validation = validation


class ConfigBase(Section):
    """ConfigBase(init=None, *, dictionary=None, **section_options)
       Config base class.
    """

    def __init__(self, init=None, *, dictionary=None, schema=None, validate=True, **section_options):
        super().__init__(dictionary=dictionary, init=init, **section_options)
        self.set_schema(schema=schema, validate=validate)

    def set_schema(self, schema, *, validate=True):
        """set_schema(self, schema, *, validate=True)
           Set the validation schema (None to disable validation).
        """
        self.schema = schema
        if validate:
            self.self_validate(raise_on_error=True)

    def self_validate(self, raise_on_error=False):
        """self_validate(self, raise_on_error=False)
           Validate the config itself using the 'schema' attribute.
        """
        if self.schema is not None:
            validation = self.schema.validate(self, raise_on_error=False)
            if raise_on_error and validation:
                raise ConfigValidationError(validation=validation)
            else:
                return validation

    @classmethod
    def get_serializer(cls, protocol):
        """get_serializer(protocol)
           Return a serializer for the required protocol.
        """
        serializer_class = Serializer.get_class(protocol)
        if serializer_class is None:
            raise ValueError("serialization protocol {} not available [{}]".format(
                protocol,
                '|'.join(registered_class.class_tag() for registered_class in Serializer.classes()),
            ))
        return serializer_class()

    def to_string(self, protocol, *, defaults=False):
        """to_string(protocol, *, defaults=False)
           Serialize to stream 'stream' according to 'protocol'.
        """
        self.self_validate(raise_on_error=True)
        serializer_instance = self.get_serializer(protocol)
        return serializer_instance.to_string(self.as_dict(defaults=defaults))

    def to_stream(self, stream, protocol, *, defaults=False):
        """to_stream(stream, protocol, *, defaults=False)
           Serialize to stream 'stream' according to 'protocol'.
        """
        self.self_validate(raise_on_error=True)
        serializer_instance = self.get_serializer(protocol)
        return serializer_instance.to_stream(self.as_dict(defaults=defaults), stream)

    def to_file(self, filename, protocol, *, defaults=False):
        """to_file(filename, protocol, *, defaults=False)
           Serialize to file 'filename' according to 'protocol'.
        """
        self.self_validate(raise_on_error=True)
        serializer_instance = self.get_serializer(protocol)
        return serializer_instance.to_file(self.as_dict(defaults=defaults), filename)

    def dump(self, stream=None, protocol="daikon", *, defaults=False):
        self.self_validate(raise_on_error=True)
        super().dump(stream=stream, protocol=protocol, defaults=defaults)

    @classmethod
    def from_file(cls, filename, protocol, *, dictionary=None, schema=None, validate=True):
        """from_file(filename, protocol, *, dictionary=None, schema=None, validate=True)
           Deserialize from file 'filename' according to 'protocol'.
        """
        serializer_instance = cls.get_serializer(protocol)
        content = serializer_instance.from_file(filename)
        instance = cls(init=content, dictionary=dictionary)
        instance.set_schema(schema=schema, validate=validate)
        return instance

    @classmethod
    def from_stream(cls, stream, protocol, *, dictionary=None, filename=None, schema=None, validate=True):
        """from_stream(stream, protocol, *, dictionary=None, filename=None, schema=None, validate=True)
           Deserialize from stream 'stream' according to 'protocol'.
        """
        serializer_instance = cls.get_serializer(protocol)
        content = serializer_instance.from_stream(stream, filename=filename)
        instance = cls(init=content, dictionary=dictionary)
        instance.set_schema(schema=schema, validate=validate)
        return instance

    @classmethod
    def from_string(cls, string, protocol, *, dictionary=None, filename=None, schema=None, validate=True):
        """from_string(string, protocol, *, dictionary=None, filename=None, schema=None, validate=True)
           Deserialize from string 'string' according to 'protocol'.
        """
        serializer_instance = cls.get_serializer(protocol)
        content = serializer_instance.from_string(string, filename=filename)
        instance = cls(init=content, dictionary=dictionary)
        instance.set_schema(schema=schema, validate=validate)
        return instance

    def read(self, filename, protocol):
        """read(filename, protocol)
           Read from file 'filename' according to 'protocol'.
        """
        self.clear()
        serializer_instance = self.get_serializer(protocol)
        content = serializer_instance.from_file(filename)
        self.update(content)
        self.self_validate(raise_on_error=True)

    def write(self, filename, protocol):
        """write(filename, protocol)
           Write to file 'filename' according to 'protocol'.
        """
        self.to_file(filename, protocol)


from .toolbox import serializer
from .toolbox.deferred import Deferred
from .toolbox.subclass import find_subclass


# deferred_expression codecs:
def _setup_codecs():
    """_setup_codecs()
       Setup codecs for validators.
    """
    def _deferred_encode(deferred_object):
        """_deferred_encode(deferred_object)
           Encoder for Deferred instances
        """
        return {'expression': deferred_object.unparse()}

    def _deferred_decode(deferred_class_name, arguments):
        """_deferred_decode(deferred_class_name, arguments)
           Decoder for Deferred instances
        """
        deferred_class = find_subclass(Deferred, deferred_class_name, include_self=True)
        if deferred_class is None:
            raise NameError("undefined Deferred class {}".format(deferred_class_name))
        return eval(arguments['expression'], {'ROOT': ROOT, 'SECTION': SECTION})  # pylint: disable=W0123

    _json_serializer_module = getattr(serializer, 'json_serializer', None)
    if _json_serializer_module is not None:
        _json_serializer_module.JSONSerializer.codec_catalog().add_codec(
            class_=Deferred,
            encode=_deferred_encode,
            decode=_deferred_decode,
        )

    _text_serializer_module = getattr(serializer, 'text_serializer', None)
    if _text_serializer_module is not None:
        _text_serializer_module.TextSerializer.codec_catalog().add_codec(
            class_=Deferred,
            encode=_deferred_encode,
            decode=_deferred_decode,
        )

        def _str_text_encode(str_object):
            """_str_text_encode(str_object)
               ConfigObj/Daikon encoder for str instances
            """
            return repr(str_object)

        def _str_text_decode(type_name, repr_data):  # pylint: disable=W0613
            """_str_text_decode(str_name, arguments)
               ConfigObj/Daikon decoder for str instances
            """
            return unrepr(repr_data, {'SECTION': SECTION, 'ROOT': ROOT})

        _text_serializer_module.TextSerializer.codec_catalog().add_codec(
            class_=str,
            encode=_str_text_encode,
            decode=_str_text_decode,
        )

_setup_codecs()

