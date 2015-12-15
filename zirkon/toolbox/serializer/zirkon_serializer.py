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
Implementation of the 'zirkon' Serializer.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'ZirkonSerializer',
]

import collections
import re

from .text_serializer import TextSerializer


def _parse_mapping(line, line_number, filename):
    """Parses a section identifier [[... section_name ...]]

       Parameters
       ----------
       line: str
           the line
       line_number: int
           the line number
       filename: str
           the file name

       Raises
       -------
       ValueError
           unparsable line

       Returns
       -------
       str
           the mapping name
    """

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
        """Returns the frame level"""
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

    def pop(self):
        """pop()"""
        self._stack.pop()

    def level(self):
        """level() -> stack level"""
        return len(self._stack) - 1

    def __len__(self):
        return len(self._stack)


class ZirkonSerializer(TextSerializer):
    """Implementation of the Zirkon serializer.
    """
    RE_INDENTATION_LINE = re.compile(r"(\s*)(.*)")

    @classmethod
    def class_tag(cls):
        return "zirkon"

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
                p_frame = None
                if len(stack) > 1:
                    p_frame = stack[-2]
                if p_frame and len(indentation) <= len(p_frame.indentation):
                    # does not belong to empty parent frame
                    stack.pop()
                    current_indentation, current_mapping, current_level = stack.get_frame_level(
                        indentation=indentation,
                        line_number=line_number,
                        filename=filename)
                else:
                    # brand new mapping
                    current_indentation = indentation
                    stack.set_indentation(index=current_level, indentation=current_indentation)
            else:
                # old mapping
                if indentation == current_indentation:
                    current_indentation, current_mapping, current_level = stack.get_frame_level(
                        indentation=indentation,
                        line_number=line_number,
                        filename=filename)
                else:
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

