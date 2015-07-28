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

"""
section
=======
Implementation of the Section class
"""

__author__ = "Simone Campagna"

import collections
import collections.abc
import re
import sys


class Section(collections.abc.Mapping):
    """Section(container, *, prefix='', init=None)
       Given the flatten mapping 'container', Section(container, prefix) implements a
       view on all the container keys starting with 'prefix'.

       >>> container = collections.OrderedDict()
       >>> section = Section(container, prefix='')
       >>> section['x_value'] = 10.1
       >>> section['y_value'] = 20.2
       >>> section['parameters'] = collections.OrderedDict((
       ...     ('alpha', 20),
       ...     ('name', 'first experiment'),
       ... ))
       >>> section['z_value'] = 30.3
       >>> section['velocity'] = collections.OrderedDict((
       ...     ('filename', 'vel.dat'),
       ...     ('type', 'RAW'),
       ... ))
       >>> section.dump()
       x_value = 10.1
       y_value = 20.2
       [parameters]
           alpha = 20
           name = 'first experiment'
       z_value = 30.3
       [velocity]
           filename = 'vel.dat'
           type = 'RAW'
       >>> del section['parameters']
       >>> section.dump()
       x_value = 10.1
       y_value = 20.2
       z_value = 30.3
       [velocity]
           filename = 'vel.dat'
           type = 'RAW'
       >>>
    """
    RE_VALID_KEY = re.compile(r"^[a-zA-Z_]\w*$")
    SUPPORTED_VALUE_TYPES = (int, float, bool, str, type(None))
    DOT = '.'
    SECTION_PLACEHOLDER = None

    def __init__(self, container, *, prefix='', init=None):
        self.container = container
        self.prefix = prefix
        if init:
            self.update(init)

    @classmethod
    def subsection_class(cls):
        """subsection_class(cls)
           Return the class to be used for subsections (it must be derived from Section)
        """
        return Section

    def subsection(self, prefix):
        """subsection(cls)
           Return a subsection with a given prefix
        """
        return self.subsection_class()(container=self.container, prefix=prefix)

    def _check_rel_key(self, rel_key):
        """_check_rel_key(self, rel_key)
           Check if 'rel_key' is correctly formed (== a valid python identifier)
        """
        if not isinstance(rel_key, str):
            raise TypeError("invalid key [{}]{} of type {}: {} keys must be strings".format(
                self.prefix,
                rel_key,
                type(rel_key).__name__,
                type(self).__name__,
            ))
        if self.DOT in rel_key:
            raise ValueError("invalid key [{}]{}: cannot contain {!r}".format(
                self.prefix,
                rel_key,
                self.DOT,
            ))
        if not self.RE_VALID_KEY.match(rel_key):
            raise ValueError("invalid key [{}]{}: invalid format".format(
                self.prefix,
                rel_key,
            ))

    def _get_abs_key(self, rel_key, check=True):
        """_get_abs_key(self, rel_key, check=True) -> abs_key
        """
        if check:
            self._check_rel_key(rel_key)
        return self.prefix + rel_key

    def _iter_keys(self):
        """_iter_keys(self) -> iterator over abs_key, rel_key
        """
        for abs_key in self.container.keys():
            if abs_key.startswith(self.prefix):
                rel_key = abs_key[len(self.prefix):]
                if rel_key:
                    yield abs_key, rel_key

    def __getitem__(self, key):
        abs_key = self._get_abs_key(key)
        if abs_key in self.container:
            return self.container[abs_key]
        else:
            sub_prefix = abs_key + self.DOT
            if sub_prefix in self.container:
                return self.subsection(prefix=sub_prefix)
        raise KeyError("undefined key [{}]{}".format(self.prefix, key))

    def __setitem__(self, key, value):
        abs_key = self._get_abs_key(key)
        sub_prefix = abs_key + self.DOT
        if isinstance(value, collections.Mapping):
            if abs_key in self.container:
                raise KeyError("cannot replace parameter [{}]{} with section".format(self.prefix, key))
            if sub_prefix in self.container:
                # remove section to remove all section keys from flattened container
                del self[key]
            subsection = self.subsection(prefix=sub_prefix)
            for sub_key, sub_value in value.items():
                subsection[sub_key] = sub_value
            self.container[sub_prefix] = self.SECTION_PLACEHOLDER
        else:
            if sub_prefix in self.container:
                raise KeyError("cannot replace section [{}]{} with parameter".format(self.prefix, key))
            if abs_key in self.container:
                del self.container[abs_key]
            if isinstance(value, self.SUPPORTED_VALUE_TYPES):
                self.container[abs_key] = value
            else:
                raise TypeError("parameter [{}]{}: invalid value {!r} of type {}".format(
                    self.prefix,
                    key,
                    value,
                    type(value).__name__,
                ))

    def __delitem__(self, key):
        abs_key = self._get_abs_key(key)
        if abs_key in self.container:
            del self.container[abs_key]
            return
        sub_prefix = abs_key + self.DOT
        if sub_prefix in self.container:
            section = self.get_section(key)
            section.clear()
            del self.container[section.prefix]
            return
        raise KeyError("missing parameter/section [{}]{}".format(self.prefix, key))

    def clear(self):
        """clear(self)
           Clear all the section content
        """
        for abs_key, _ in self._iter_keys():
            if len(abs_key) > len(self.prefix):
                del self.container[abs_key]

    def get(self, key, default=None):
        abs_key = self._get_abs_key(key)
        if abs_key in self.container:
            return self.container[abs_key]
        else:
            sub_prefix = abs_key + self.DOT
            if sub_prefix in self.container:
                return self.subsection(prefix=sub_prefix)
        return default

    def get_parameter(self, parameter_name, default=None):
        """get_parameter(self, parameter_name, default=None) -> value
           Get a parameter (raises KeyError if a section is found)
        """
        abs_key = self._get_abs_key(parameter_name)
        sub_prefix = abs_key + self.DOT
        if sub_prefix in self.container:
            raise KeyError("[{}]{} is a section, not a parameter".format(self.prefix, parameter_name))
        return self.container.get(abs_key, default)

    def get_section(self, section_name, default=None):
        """get_section(self, section_name, default=None) -> value
           Get a section (raises KeyError if a parameter is found)
        """
        abs_key = self._get_abs_key(section_name)
        if abs_key in self.container:
            raise KeyError("[{}]{} is a parameter, not a section".format(self.prefix, section_name))
        sub_prefix = abs_key + self.DOT
        if sub_prefix in self.container:
            return self.subsection(prefix=sub_prefix)
        else:
            return default

    def has_parameter(self, parameter_name):
        """has_parameter(self, parameter_name) -> bool
           Return True if parameter exists (raises KeyError if a section is found)
        """
        return self._get_abs_key(parameter_name) in self.container

    def has_section(self, section_name):
        """get_section(self, section_name) -> bool
           Return True if section exists (raises KeyError if a parameter is found)
        """
        return self._get_abs_key(section_name) + self.DOT in self.container

    def __contains__(self, key):
        abs_key = self._get_abs_key(key)
        return abs_key in self.container or abs_key + self.DOT in self.container

    def __len__(self):
        count = 0
        for _, rel_key in self._iter_keys():
            dot_index = rel_key.find(self.DOT)
            if dot_index == len(rel_key) - 1 or dot_index < 0:
                count += 1
        return count

    def parameters(self):
        """parameters(self) -> parameter items
           Iterator over parameter items
        """
        for abs_key, rel_key in self._iter_keys():
            dot_index = rel_key.find(self.DOT)
            if dot_index < 0:
                yield rel_key, self.container[abs_key]

    def sections(self):
        """sections(self) -> section items
           Iterator over section items
        """
        for abs_key, rel_key in self._iter_keys():
            dot_index = rel_key.find(self.DOT)
            if dot_index == len(rel_key) - 1:
                yield rel_key[:-1], self.subsection(prefix=abs_key)

    def items(self):
        for abs_key, rel_key in self._iter_keys():
            dot_index = rel_key.find(self.DOT)
            if dot_index < 0:
                yield rel_key, self.container[abs_key]
            elif dot_index == len(rel_key) - 1:
                yield rel_key[:-1], self.subsection(prefix=abs_key)

    def keys(self):
        for rel_key, _ in self.items():
            yield rel_key

    def __iter__(self):
        for rel_key, _ in self.items():
            yield rel_key

    def values(self):
        for _, value in self.items():
            yield value

    def dump(self, stream=None, *, indentation=""):
        """dump(self, stream=None, *, indentation="")
           Dump the content to a stream
        """
        if stream is None:
            stream = sys.stdout
        for rel_key, value in self.items():
            if isinstance(value, Section):
                stream.write("{}[{}]\n".format(indentation, rel_key))
                value.dump(stream=stream, indentation=indentation + "    ")
            else:
                stream.write("{}{} = {!r}\n".format(indentation, rel_key, value))

    def update(self, mapping):
        """update(self, mapping)
           Update with the content of the 'mapping'
        """
        for key, value in mapping.items():
            self[key] = value

    def as_dict(self, *, dict_class=collections.OrderedDict):
        """as_dict(self, *, dict_class=collections.OrderedDict) -> dict
           Return a dict with all the section content
        """
        result = dict_class()
        for rel_key, value in self.items():
            if isinstance(value, Section):
                result[rel_key] = value.as_dict(dict_class=dict_class)
            else:
                result[rel_key] = value
        return result

    def __repr__(self):
        return "{}(container={!r}, prefix={!r})".format(self.__class__.__name__, self.container, self.prefix)

    def __str__(self):
        data = []
        for key, value in self.items():
            if isinstance(value, Section):
                data.append((key, str(value)))
            else:
                data.append((key, repr(value)))
        content = ', '.join("{}={}".format(k, v) for k, v in data)
        return "{}({})".format(self.__class__.__name__, content)

    def __eq__(self, section):
        if isinstance(section, Section) and section.container is self.container:
            return section.prefix == self.prefix
        else:
            for key, value in self.items():
                if key not in section:
                    return False
                if value != section[key]:
                    return False
            for key, value in section.items():
                if key not in self:
                    return False
                if self[key] != value:
                    return False
            return True

