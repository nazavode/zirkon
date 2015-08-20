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
Implementation of the TextSerializer base class for text serializers.
"""

__author__ = "Simone Campagna"
__all__ = [
    'TextSerializer',
]

import abc
import collections
import re

from .codec_catalog import CodecCatalog
from .serializer import Serializer
from ..unrepr import unrepr


class TextSerializer(Serializer):
    """Implementation of the Text abstract serializer.
    """
    CODEC_CATALOG = CodecCatalog()
    RE_FUNC = re.compile(r'\s*(?P<func_name>\w+)\(.*')
    INDENTATION = "    "

    def indentation(self, level):
        """Returns the indentation for a given level

           Parameters
           ----------
           level: int
               the indentation level

           Returns
           -------
           str
               the indentation string
        """
        return self.INDENTATION * level

    def encode_value(self, value):
        """Encodes a value to a string, using a codec or repr.

           Parameters
           ----------
           value: any
               the value to be encoded

           Returns
           -------
           str
               the string encoding
        """
        value_type = type(value)
        codec = self.CODEC_CATALOG.get_by_class(value_type)
        if codec is None:
            value = repr(value)
        else:
            value = codec.encode(value)
        return value

    def decode_value(self, line_number, filename, key, value, *value_type_names):  # pylint: disable=W0613
        r"""Decodes a value from a string, using a codec or unrepr.

             Parameters
             ----------
             line_number: int
                 the line number
             filename: str
                 the file name
             key: str
                 the key name
             value: any
                 the encoded value
             \*value_type_names: tuple
                 a list of type names to be used to find a codec

             Returns
             -------
             any
                 the decoded value
        """
        if value_type_names:
            for value_type_name in value_type_names:
                codec = self.CODEC_CATALOG.get_by_name(value_type_name)
                if codec is not None:
                    return codec.decode(value_type_name, value)
            raise ValueError("line {}@{}: cannot decode value {!r} according to value types {}".format(
                line_number,
                filename,
                value,
                ', '.join(value_type_names)))
        else:
            try:
                return unrepr(value)
            except Exception as err:
                raise ValueError("line {}@{}: invalid value {!r}: {}: {}".format(
                    line_number, filename, value, type(err).__name__, err))

    def impl_dump_key_value(self, level, key, value):
        """Returns the line for a the key/value pair.

           Parameters
           ----------
           level: int
               the nesting level
           key: str
               the key name
           value: any
               the key value

           Returns
           -------
           str
               the key=value line
        """
        return "{i}{k} = {v}".format(
            i=self.indentation(level),
            k=key,
            v=value,
        )

    @abc.abstractmethod
    def impl_dump_mapping_name(self, level, mapping_name):
        """Returns a line for a mapping name.

           Parameters
           ----------
           level: int
               the nesting level
           mapping_name: str
               the mapping name

           Returns
           -------
           str
               the mapping name line
        """
        raise NotImplementedError

    def impl_dump_mapping(self, level, lines, mapping_name, mapping):
        """Generates and appends lines for a mapping.

           Parameters
           ----------
           level: int
               the nesting level
           lines: list
               the list of lines
           mapping_name: str
               the mapping name
           mapping: str
               the mapping
        """
        lines.append(self.impl_dump_mapping_name(level=level, mapping_name=mapping_name))
        self.impl_dump_mapping_lines(level=level + 1, lines=lines, mapping=mapping)

    @abc.abstractmethod
    def impl_iter_mapping_items(self, mapping):
        """Iterates over mapping items

           Parameters
           ----------
           mapping: str
               the mapping

           Returns
           -------
           iterator
               iterator over mapping items
        """
        raise NotImplementedError

    def impl_dump_mapping_lines(self, level, lines, mapping):
        """Generates and appends lines for a mapping serialization

           Parameters
           ----------
           level: int
               the nesting level
           lines: list
               the list of lines
           mapping: str
               the mapping
        """
        for key, value in self.impl_iter_mapping_items(mapping):
            if isinstance(value, collections.Mapping):
                self.impl_dump_mapping(level=level, lines=lines, mapping_name=key, mapping=value)
            else:
                encoded_value = self.encode_value(value)
                lines.append(self.impl_dump_key_value(level=level, key=key, value=encoded_value))

    def to_string(self, obj):
        if not isinstance(obj, collections.Mapping):
            raise TypeError("{}: cannot serializer object of type {}: not a Mapping".format(
                type(self).__name__, type(obj).__name__))
        lines = []
        self.impl_dump_mapping_lines(level=0, lines=lines, mapping=obj)
        if lines:
            return '\n'.join(lines) + '\n'
        else:
            return ''

    def impl_parse_key_value(self, line, line_number, filename):
        """Parses a key/value line

           Parameters
           ----------
           line: str
               the key/value line
           line_number: int
               the line number
           filename: str
               the file name

           Returns
           -------
           tuple
               (key, value)
        """
        # key:
        l_kv = line.split('=', 1)
        if len(l_kv) < 2:
            raise ValueError("unparsable line {}@{}: {!r}".format(
                line_number, filename, line))
        key, value = line.split('=', 1)
        value = value.strip()
        match = self.RE_FUNC.match(value)
        value_type_names = []
        if match:
            value_type_name = match.groupdict()['func_name']
            value_type_names.append(value_type_name)
        value_type_names.append('str')
        value = self.decode_value(line_number, filename, key, value, *value_type_names)
        return key.strip(), value

    def from_string(self, serialization, *, filename=None):
        if filename is None:
            filename = '<string>'
        return self.impl_from_string(collections.OrderedDict, serialization, filename=filename)

    @abc.abstractmethod
    def impl_from_string(self, dct_class, serialization, *, filename=None):
        """Implementation of the from_string method.

           Parameters
           ----------
           dct_class: type
               the dict class to be used
           serialization: str
               the serialization
           filename: str
               the file name

           Returns
           -------
           any
               the deserialized object
        """
        raise NotImplementedError
