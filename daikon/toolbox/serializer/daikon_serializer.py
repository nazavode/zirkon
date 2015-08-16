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


def _parse_mapping(line, line_number, filename):
    """_parse_mapping(line, line_number, filename) -> mapping_name"""

    if line[0] == '[' and line[-1] == ']':
        line = line[1:-1]
    if line[0] == '[' or line[-1] == ']':
        raise ValueError("invalid line {}@{}: unbalanced []".format(line_number, filename))
    return line.strip()


_FrameInfo = collections.namedtuple("_FrameInfo", ("indentation", "mapping"))


class _Stack(object):
    """Indentation/mapping stack management"""
    def __init__(self):
        self._stack = []

    def __getitem__(self, index):
        return self._stack[index]

    def __delitem__(self, index):
        del self._stack[index]

    def get_frame_level(self, indentation, line_number, filename):
        """get_frame_level(indentation, line_number, filename) -> indentation, mapping, level"""
        for level, frame_info in enumerate(self._stack):
            if frame_info.indentation == indentation:
                del self[level + 1:]
                return tuple(self._stack[-1]) + (self.level(),)
        raise IndentationError("line {}@{}: unmatching indentation".format(line_number, filename))

    def set_indentation(self, index, indentation):
        """set_indentation(index, indentation)"""
        frame_info = self._stack[index]
        assert frame_info.indentation is None
        self._stack[index] = frame_info._replace(indentation=indentation)

    def push(self, mapping):
        """push(mapping)"""
        frame_info = _FrameInfo(
            indentation=None,
            mapping=mapping)
        self._stack.append(frame_info)
        return tuple(frame_info) + (self.level(),)

    def level(self):
        """level() -> stack level"""
        return len(self._stack) - 1

    def __len__(self):
        return len(self._stack)


class DaikonSerializer(TextSerializer):
    """DaikonSerializer()
       Implementation of the Daikon serializer.
    """
    RE_INDENTATION_LINE = re.compile(r"(\s*)(.*)")

    @classmethod
    def class_tag(cls):
        return "daikon"

    def impl_dump_mapping_name(self, level, mapping_name):
        return "{i}{b}{s}{k}".format(
            i=self.indentation(level),
            b='[',
            s=mapping_name,
            k=']',
        )

    def impl_iter_mapping_items(self, mapping):
        # interspersed keys and mappings
        yield from mapping.items()

    def impl_from_string(self, dct_class, serialization, *, filename=None):
        dct = dct_class()
        stack = _Stack()
        current_indentation, current_mapping, current_level = stack.push(dct)
        for line_number, source_line in enumerate(serialization.split('\n')):
            indentation, line = self.RE_INDENTATION_LINE.match(source_line).groups()
            if not line or line[0] == '#':
                # empty line or comment
                continue
            if current_indentation is None:
                # brand new mapping
                current_indentation = indentation
                stack.set_indentation(index=current_level, indentation=current_indentation)
            else:
                # old mapping
                if indentation != current_indentation:
                    if indentation.startswith(current_indentation):
                        raise IndentationError("line {}@{}: unexpected indentation".format(line_number, filename))
                    else:
                        current_indentation, current_mapping, current_level = stack.get_frame_level(
                            indentation=indentation,
                            line_number=line_number,
                            filename=filename)
            if line[0] == '[':
                # mapping
                mapping_name = _parse_mapping(line, line_number, filename)
                current_mapping[mapping_name] = dct_class()
                current_indentation, current_mapping, current_level = stack.push(current_mapping[mapping_name])
                current_level = len(stack) - 1
            else:
                # key:
                key, value = self.impl_parse_key_value(line=line, line_number=line_number, filename=filename)
                current_mapping[key] = value
        return dct

