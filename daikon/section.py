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
daikon.section
==============
Implementation of the Section class
"""

__author__ = "Simone Campagna"
__all__ = [
    'Section',
]

import collections
import collections.abc
import sys

from .toolbox.identifier import is_valid_identifier
from .toolbox.dictutils import compare_dicts
from .toolbox.serializer import Serializer

class Section(collections.abc.Mapping):
    """Section(*, dictionary=None, init=None)
       Dictionary-like object implementing storage of parameters/sections. The
       internal representation is stored onto a standard dictionary, which can
       be provided in construction.

       >>> section = Section()
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
    SUPPORTED_DATA_TYPES = (int, float, bool, str, type(None), list, tuple)

    def __init__(self, *, dictionary=None, init=None):
        if dictionary is None:
            dictionary = self.dictionary_factory()
        self.dictionary = dictionary
        if init:
            self.update(init)

    @classmethod
    def dictionary_factory(cls):
        """dctionary_factory() -> new (empty) dictionary
           Factory for new dictionaries.
        """
        return collections.OrderedDict()

    @classmethod
    def subsection_class(cls):
        """subsection_class(cls)
           Return the class to be used for subsections (it must be derived from Section)
        """
        return Section

    def subsection(self, dictionary):
        """subsection(self, *p_args, **n_args)
           Return a subsection with the given name
        """
        return self.subsection_class()(dictionary=dictionary)

    def __getitem__(self, key):
        value = self.dictionary[key]
        if isinstance(value, collections.Mapping):
            return self.subsection(dictionary=value)
        else:
            if isinstance(value, self.SUPPORTED_DATA_TYPES):
                return value
            else:
                raise TypeError("parameter {}: invalid value {!r} of type {}".format(
                    key,
                    value,
                    type(value).__name__,
                ))

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("invalid key {!r} of non-string type {}".format(key, type(key).__name__))
        elif not is_valid_identifier(key):
            raise ValueError("invalid key {!r}: malformed identifier".format(key))
        if isinstance(value, collections.Mapping):
            if self.has_parameter(key):
                raise TypeError("parameter {} cannot be replaced with a section".format(key))
            dictionary = self.dictionary_factory()
            dictionary.update(value)
            value = dictionary
        else:
            if not isinstance(value, self.SUPPORTED_DATA_TYPES):
                raise TypeError("parameter {}: invalid value {!r} of type {}".format(
                    key,
                    value,
                    type(value).__name__,
                ))
            if self.has_section(key):
                raise TypeError("section {} cannot be replaced with a parameter".format(key))
        self.dictionary[key] = value

    def __delitem__(self, key):
        del self.dictionary[key]

    def clear(self):
        """clear()
           Clear all the section's content.
        """
        self.dictionary.clear()

    def copy(self):
        """copy()
           Returns a deep copy of the section.
        """
        return self.subsection_class()(dictionary=self.dictionary.copy())

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def get_parameter(self, parameter_name, default=None):
        """get_parameter(self, parameter_name, default=None) -> value
           Get a parameter (raises KeyError if a section is found)
        """
        if not parameter_name in self.dictionary:
            return default
        else:
            value = self.dictionary[parameter_name]
            if isinstance(value, collections.Mapping):
                raise KeyError("{} is a section, not a parameter".format(parameter_name))
            return value

    def get_section(self, section_name, default=None):
        """get_section(self, section_name, default=None) -> value
           Get a section (raises KeyError if a parameter is found)
        """
        if not section_name in self.dictionary:
            return default
        else:
            value = self.dictionary[section_name]
            if not isinstance(value, collections.Mapping):
                raise KeyError("{} is a parameter, not a section".format(section_name))
            value = self.subsection(dictionary=value)
            return value

    def has_parameter(self, parameter_name):
        """has_parameter(self, parameter_name) -> bool
           Return True if parameter exists.
        """
        return parameter_name in self.dictionary and \
            not isinstance(self.dictionary[parameter_name], collections.Mapping)

    def has_section(self, section_name):
        """has_section(self, section_name) -> bool
           Return True if section exists.
        """
        return section_name in self.dictionary and \
            isinstance(self.dictionary[section_name], collections.Mapping)

    def parameters(self):
        """parameters(self) -> parameter items
           Iterator over parameter items
        """
        for key, value in self.items():
            if not isinstance(value, collections.Mapping):
                yield key, value

    def sections(self):
        """sections(self) -> section items
           Iterator over section items
        """
        for key, value in self.items():
            if isinstance(value, collections.Mapping):
                yield key, value

    def items(self):
        for key, value in self.dictionary.items():
            if isinstance(value, collections.Mapping):
                value = self.subsection(dictionary=value)
            yield key, value

    def keys(self):
        for key, _ in self.items():
            yield key

    def values(self):
        for _, value in self.items():
            yield value

    def __contains__(self, key):
        return key in self.dictionary

    def __len__(self):
        return len(self.dictionary)

    def __iter__(self):
        yield from self.keys()

    def update(self, dictionary):
        """update(self, dictionary)
           Update with the content of the 'dictionary'
        """
        for key, value in dictionary.items():
            self[key] = value

    def as_dict(self, *, dict_class=collections.OrderedDict):
        """as_dict(self, *, dict_class=collections.OrderedDict) -> dict
           Return a dict with all the section content
        """
        result = dict_class()
        subsection_class = self.subsection_class()
        for key, value in self.items():
            if isinstance(value, subsection_class):
                result[key] = value.as_dict(dict_class=dict_class)
            else:
                result[key] = value
        return result

    def __repr__(self):
        return "{}(dictionary={!r})".format(self.__class__.__name__, self.dictionary)

    def __str__(self):
        data = []
        subsection_class = self.subsection_class()
        for key, value in self.items():
            if isinstance(value, subsection_class):
                data.append((key, str(value)))
            else:
                data.append((key, repr(value)))
        content = ', '.join("{}={}".format(k, v) for k, v in data)
        return "{}({})".format(self.__class__.__name__, content)

    def __eq__(self, section):
        if isinstance(section, Section):
            return compare_dicts(section.dictionary, self.dictionary)
        else:
            for key, value in self.items():
                if key not in section:
                    print("A {!r}={!r}".format(key, value))
                    return False
                if value != section[key]:
                    print("B {!r}={!r}".format(key, value))
                    return False
            for key, value in section.items():
                if key not in self:
                    print("C {!r}={!r}".format(key, value))
                    return False
                if self[key] != value:
                    print("D {!r}={!r}".format(key, value))
                    return False
            return True

    def __bool__(self):
        for _ in self.items():
            return True
        return False

    def dump(self, stream=None, protocol="Daikon"):
        """dump(self, stream=None, protocol="Daikon")
           Dump the content to a stream.
        """
        if stream is None:
            stream = sys.stdout
        serializer = Serializer.get_class(protocol)()
        serializer.to_stream(stream=stream, config=self)
