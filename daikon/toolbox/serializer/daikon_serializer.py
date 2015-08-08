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
config.toolbox.serializer.daikon_serializer
==============================================
Implementation of the Daikon Serializer
"""

__author__ = "Simone Campagna"
__all__ = [
    'DaikonSerializer',
]

import collections
import re

from .text_serializer import TextSerializer
from ..unrepr import unrepr


def _parse_section(line, line_number, filename):
    """_parse_section(line, line_number, filename) -> section_name"""

    if line[0] == '[' and line[-1] == ']':
        line = line[1:-1]
    if line[0] == '[' or line[-1] == ']':
        raise ValueError("invalid line {}@{}: unbalanced []".format(line_number, filename))
    return line.strip()


class DaikonSerializer(TextSerializer):
    """DaikonSerializer()
       Implementation of the Daikon serializer.
    """
    RE_FUNC = re.compile(r'\s*(?P<func_name>\w+)\(.*')
    INDENTATION = '    '

    @classmethod
    def class_tag(cls):
        return "Daikon"

    def indentation(self, level):
        """indentation(level) -> indentation string"""
        return self.INDENTATION * level

    def impl_dump_key_value(self, level, key, value):
        return "{i}{k} = {v}".format(
            i=self.indentation(level),
            k=key,
            v=value,
        )

    def impl_dump_section_name(self, level, section_name):
        return "{i}{b}{s}{k}".format(
            i=self.indentation(level),
            b='[',
            s=section_name,
            k=']',
        )

    def impl_dump_section_lines(self, level, lines, section):
        def dump_section(level, lines, section_name, section):
            lines.append(self.impl_dump_section_name(level=level, section_name=section_name))
            self.impl_dump_section_lines(level=level + 1, lines=lines, section=section)

        for key, value in section.items():
            if isinstance(value, collections.Mapping):
                dump_section(level=level, lines=lines, section_name=key, section=value)
            else:
                encoded_value = self.encode_value(value)
                lines.append(self.impl_dump_key_value(level=level, key=key, value=encoded_value))

    def from_string(self, config_class, serialization, *, dictionary=None, filename=None):
        if filename is None:
            filename = '<string>'
        config = config_class(dictionary=dictionary)
        indentation_section_stack = [(None, config)]
        (current_indentation, current_section) = indentation_section_stack[-1]
        current_level = len(indentation_section_stack) - 1
        re_indent = re.compile(r"(\s*)(.*)")
        for line_number, source_line in enumerate(serialization.split('\n')):
            indentation, line = re_indent.match(source_line).groups()
            if not line or line[0] == '#':
                # empty line or comment
                continue
            if current_indentation is None:
                # brand new section
                current_indentation = indentation
                indentation_section_stack[current_level] = (current_indentation, current_section)
            else:
                # old section
                if indentation != current_indentation:
                    if indentation.startswith(current_indentation):
                        raise IndentationError("line {}@{}: unexpected indentation".format(line_number, filename))
                    else:
                        for o_level, (o_indentation, o_section) in enumerate(indentation_section_stack):
                            if o_indentation == indentation:
                                level = o_level
                                del indentation_section_stack[level + 1:]
                                (current_indentation, current_section) = indentation_section_stack[-1]
                                break
                        else:
                            raise IndentationError("line {}@{}: unmatching indentation".format(line_number, filename))
            if line[0] == '[':
                # section
                section_name = _parse_section(line, line_number, filename)
                current_section[section_name] = {}
                indentation_section_stack.append((None, current_section[section_name]))
                current_indentation, current_section = indentation_section_stack[-1]
                current_level = len(indentation_section_stack) - 1
            else:
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
                value = self.decode_value(line_number, filename, key, value, *value_type_names)
                current_section[key.strip()] = value
        return config

