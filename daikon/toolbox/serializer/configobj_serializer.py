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


from .text_serializer import TextSerializer


def _parse_mapping(line, line_number, filename):
    """_parse_mapping(line, line_number, filename) -> mapping level, name"""

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

    @classmethod
    def class_tag(cls):
        return "ConfigObj"

    def impl_dump_mapping_name(self, level, mapping_name):
        return "{i}{b}{s}{k}".format(
            i=self.indentation(level),
            b='[' * (level + 1),
            s=mapping_name,
            k=']' * (level + 1),
        )

    def impl_iter_mapping_items(self, mapping):
        # keys before, mappings after
        if self.is_section(mapping):
            yield from mapping.parameters()
            yield from mapping.sections()
        else:
            yield from mapping.items()

    def impl_from_string(self, config, serialization, *, filename=None):
        mapping_stack = [config]
        current_mapping, current_level = mapping_stack[-1], len(mapping_stack) - 1
        for line_number, source_line in enumerate(serialization.split('\n')):
            line = source_line.strip()
            if not line or line[0] == '#':
                # empty line or comment
                continue
            if line[0] == '[':
                # mapping
                level, mapping_name = _parse_mapping(line, line_number, filename)
                if level <= current_level + 1:
                    del mapping_stack[level:]
                    current_mapping, current_level = mapping_stack[-1], len(mapping_stack) - 1
                else:
                    raise ValueError("invalid value at line {}@{}: invalid mapping level {}".format(
                        line_number, filename, level))
                current_mapping[mapping_name] = {}
                mapping_stack.append(current_mapping[mapping_name])
                current_mapping, current_level = mapping_stack[-1], len(mapping_stack) - 1
            else:
                # key:
                key, value = self.impl_parse_key_value(line=line, line_number=line_number, filename=filename)
                current_mapping[key] = value
        return config

