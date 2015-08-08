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

from .serializer import Serializer
from ..unrepr import unrepr


class TextSerializer(Serializer):
    """TextSerializer()
       Implementation of the ConfigObj serializer.
    """

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

    @abc.abstractmethod
    def impl_dump_key_value(self, level, key, value):
        """impl_dump_key_value(level, key, value) -> line"""
        pass

    @abc.abstractmethod
    def impl_dump_section_name(self, level, section_name):
        """impl_dump_section_name(level, section_name) -> line"""
        pass

    def impl_dump_section_lines(self, level, lines, section):
        """dump_section(level, lines, section)
           Writes lines for the 'section' serialization'
        """
        def dump_section(level, lines, section_name, section):
            lines.append(self.impl_dump_section_name(level=level, section_name=section_name))
            self.impl_dump_section_lines(level=level + 1, lines=lines, section=section)

        for key, value in section.parameters():
            value = self.encode_value(value)
            if isinstance(value, collections.Mapping):
                dump_section(level=level, lines=lines, section_name=key, section=value)
            else:
                lines.append(self.impl_dump_key_value(level=level, key=key, value=value))
        for key, value in section.sections():
            dump_section(level=level, lines=lines, section_name=key, section=value)

    def to_string(self, config):
        lines = []
        self.impl_dump_section_lines(level=0, lines=lines, section=config)
        return '\n'.join(lines) + '\n'

