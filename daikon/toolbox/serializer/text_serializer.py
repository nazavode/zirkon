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
config.toolbox.serializer.text_serializer
=========================================
Implementation of the TextSerializer base class for text serializers
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
    """TextSerializer()
       Implementation of the ConfigObj serializer.
    """
    CODEC_CATALOG = CodecCatalog()

    @classmethod
    def class_tag(cls):
        return "ConfigObj"

    def encode_value(self, value):
        """encode_value(key, value) -> encoded value"""
        value_type = type(value)
        codec = self.CODEC_CATALOG.get_by_class(value_type)
        if codec is None:
            value = repr(value)
        else:
            value = codec.encode(value)
        return value

    def decode_value(self, line_number, filename, key, value, *value_type_names):
        """decode_value(line_number, filename, key, value) -> decoded value"""
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


    @abc.abstractmethod
    def impl_dump_key_value(self, level, key, value):
        """impl_dump_key_value(level, key, value) -> line"""
        pass

    @abc.abstractmethod
    def impl_dump_section_name(self, level, section_name):
        """impl_dump_section_name(level, section_name) -> line"""
        pass

    def impl_dump_section_lines(self, level, lines, section):
        """impl_dump_section(level, lines, section)
           Writes lines for the 'section' serialization'
        """
        def dump_section(level, lines, section_name, section):
            lines.append(self.impl_dump_section_name(level=level, section_name=section_name))
            self.impl_dump_section_lines(level=level + 1, lines=lines, section=section)

        for key, value in section.parameters():
            if isinstance(value, collections.Mapping):
                dump_section(level=level, lines=lines, section_name=key, section=value)
            else:
                encoded_value = self.encode_value(value)
                lines.append(self.impl_dump_key_value(level=level, key=key, value=encoded_value))
        for key, value in section.sections():
            dump_section(level=level, lines=lines, section_name=key, section=value)

    def to_string(self, config):
        lines = []
        self.impl_dump_section_lines(level=0, lines=lines, section=config)
        return '\n'.join(lines) + '\n'

