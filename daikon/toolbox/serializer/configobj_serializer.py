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
config.toolbox.serializer.configobj_serializer
==============================================
Implementation of the ConfigObj Serializer
"""

__author__ = "Simone Campagna"
__all__ = [
    'ConfigObjSerializer',
]

import re

from .text_serializer import TextSerializer
from ..unrepr import unrepr


def _parse_section(line, line_number, filename):
    """_parse_section(line, line_number, filename) -> section level, name"""

    level = 0
    while line:
        if line[0] == '[' and line[-1] == ']':
            level += 1
            line = line[1:-1]
            continue
        else:
            break
    if line[0] == '[' or line[-1] == ']':
        raise ValueError("invalid line {}@{}: unbalanced []".format(line_number, filename))
    return level, line.strip()


class ConfigObjSerializer(TextSerializer):
    """ConfigObjSerializer()
       Implementation of the ConfigObj serializer.
    """
    RE_FUNC = re.compile(r'\s*(?P<func_name>\w+)\(.*')
    INDENTATION = '    '

    @classmethod
    def class_tag(cls):
        return "ConfigObj"

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
            b='[' * (level + 1),
            s=section_name,
            k=']' * (level + 1),
        )

    def from_string(self, config_class, serialization, *, dictionary=None, filename=None):
        if filename is None:
            filename = '<string>'
        config = config_class(dictionary=dictionary)
        section_stack = [config]
        current_section, current_level = section_stack[-1], len(section_stack) - 1
        for line_number, source_line in enumerate(serialization.split('\n')):
            line = source_line.strip()
            if not line or line[0] == '#':
                # empty line or comment
                continue
            if line[0] == '[':
                # section
                level, section_name = _parse_section(line, line_number, filename)
                if level <= current_level + 1:
                    del section_stack[level:]
                    current_section, current_level = section_stack[-1], len(section_stack) - 1
                else:
                    raise ValueError("invalid value at line {}@{}: invalid section level {}".format(
                        line_number, filename, level))
                current_section[section_name] = {}
                section_stack.append(current_section[section_name])
                current_section, current_level = section_stack[-1], len(section_stack) - 1
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

