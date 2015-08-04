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
config.serializer.configobj_serializer
======================================
Implementation of the ConfigObj Serializer
"""

__author__ = "Simone Campagna"
__all__ = [
    'update_globals',
    'ConfigObjSerializer',
]

from .serializer import Serializer

_EVAL_GLOBALS = {}


def update_globals(dct):
    """update_globals()
       Update globals to be used when evaluating config values.
    """
    _EVAL_GLOBALS.update(dct)


class ConfigObjSerializer(Serializer):
    """JSONSerializer()
       Implementation of the ConfigObj serializer.
    """

    CONFIGOBJ_OPTIONS = dict(
        interpolation=False,
        unrepr=True,
    )

    @classmethod
    def plugin_name(cls):
        return "ConfigObj"

    def _dump_section(self, lines, section, indentation_level=0, indentation="    "):
        """_dump_section(lines, section, indentation_level=0, indentation="    ")
           Writes lines for the 'section' serialization'
        """
        ind = indentation * indentation_level
        for key, value in section.parameters():
            lines.append("{}{} = {!r}".format(ind, key, value))
        for key, value in section.sections():
            left = "[" * (indentation_level + 1)
            right = "]" * (indentation_level + 1)
            lines.append(ind + left + key + right)
            self._dump_section(lines, value, indentation_level=indentation_level + 1, indentation=indentation)

    def to_string(self, config):
        lines = []
        self._dump_section(lines, config)
        return '\n'.join(lines) + '\n'

    def from_string(self, config_class, serialization, *, container=None, prefix='', filename=None):
        if filename is None:
            filename = '<string>'
        config = config_class(container=container, prefix=prefix)
        section_stack = [config]
        current_section, current_level = section_stack[-1], len(section_stack) - 1
        for line_no, source_line in enumerate(serialization.split('\n')):
            line = source_line.strip()
            if not line or line[0] == '#':
                # empty line or comment
                continue
            if line[0] == '[':
                # section
                level = 0
                while line:
                    if line[0] == '[' and line[-1] == ']':
                        level += 1
                        line = line[1:-1]
                        continue
                    else:
                        break
                if level <= current_level + 1:
                    del section_stack[level:]
                    current_section, current_level = section_stack[-1], len(section_stack) - 1
                else:
                    raise ValueError("invalid value at line {}@{}: invalid section level {}".format(
                        line_no, filename, level))
                section_name = line.strip()
                current_section[section_name] = {}
                section_stack.append(current_section[section_name])
                current_section, current_level = section_stack[-1], len(section_stack) - 1
            else:
                # key:
                key, val = line.split('=', 1)
                try:
                    current_section[key.strip()] = eval(val, _EVAL_GLOBALS)  # pylint: disable=W0123
                except Exception as err:
                    raise ValueError("invalid value at line {}@{}: {}: {}".format(
                        line_no, filename, type(err).__name__, err))
        return config

