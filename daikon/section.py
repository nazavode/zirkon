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
    'iter_section_options',
    'count_section_options',
    'has_section_options',
]

import collections
import collections.abc
import sys

from .toolbox.deferred import Deferred
from .toolbox.dictutils import as_dict
from .toolbox.identifier import is_valid_identifier
from .toolbox.serializer import Serializer


class Section(collections.abc.Mapping):
    """Section(init=None, *, dictionary=None, parent=None)
       Dictionary-like object implementing storage of options/sections. The
       internal representation is stored onto a standard dictionary, which can
       be provided in construction.

       >>> section = Section()
       >>> section['x_value'] = 10.1
       >>> section['y_value'] = 20.2
       >>> section['data'] = collections.OrderedDict((
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
       [data]
           alpha = 20
           name = 'first experiment'
       z_value = 30.3
       [velocity]
           filename = 'vel.dat'
           type = 'RAW'
       >>> del section['data']
       >>> section.dump()
       x_value = 10.1
       y_value = 20.2
       z_value = 30.3
       [velocity]
           filename = 'vel.dat'
           type = 'RAW'
       >>>
    """
    SUPPORTED_SEQUENCE_TYPES = (list, tuple)
    SUPPORTED_SCALAR_TYPES = (int, float, bool, str, type(None))

    def __init__(self, init=None, *, dictionary=None, parent=None):
        if dictionary is None:
            dictionary = self._dictionary_factory()
        self.dictionary = dictionary
        if parent is None:
            self.parent = self
            self.root = self
        else:
            self.parent = parent
            self.root = self.parent.root
        # the reference section for ROOT and SECTION:
        self._ref_section = None
        if init:
            self.update(init)

    @property
    def ref_section(self):
        """ref_section property getter"""
        return self._ref_section

    @ref_section.setter
    def ref_section(self, section):
        """ref_section property setter"""
        if self._ref_section is not None and section is not None and self._ref_section is not section:
            raise TypeError("reference section already set")
        self._ref_section = section

    @classmethod
    def _subsection_class(cls):
        """_subsection_class(cls)
           Return the class to be used for subsections (it must be derived from Section)
        """
        return Section

    def _subsection(self, section_name, dictionary):
        """_subsection(self, section_name, dictionary)
           Return a subsection with the given name
        """
        dummy = section_name
        return self._subsection_class()(dictionary=dictionary, parent=self)

    @classmethod
    def _dictionary_factory(cls):
        """_dictionary_factory() -> new (empty) dictionary
           Factory for new dictionaries.
        """
        return collections.OrderedDict()

    def _evaluate(self, value, ref_section=None):
        """_evaluate(value)
        """
        if isinstance(value, Deferred):
            if ref_section is None:
                ref_section = self._ref_section
            if ref_section is None:
                ref_section = self
            value = value.evaluate({'SECTION': ref_section, 'ROOT': ref_section.root})
        return value

    def _check_option(self, key, value):
        """_check_option(key, value)
        """
        if isinstance(value, self.SUPPORTED_SCALAR_TYPES):
            return value
        elif isinstance(value, self.SUPPORTED_SEQUENCE_TYPES):
            for index, item in enumerate(value):
                if not isinstance(item, self.SUPPORTED_SCALAR_TYPES):
                    fmt = "option {key}: invalid {value_type}: item #{index} {item!r} has invalid type {item_type}"
                    raise TypeError(fmt.format(
                        key=key,
                        value_type=type(value).__name__,
                        index=index,
                        item=item,
                        item_type=type(item).__name__,
                    ))
            return value
        else:
            raise TypeError("option {}: invalid value {!r} of type {}".format(
                key,
                value,
                type(value).__name__,
            ))

    def __getitem__(self, key):
        value = self.dictionary[key]
        if isinstance(value, collections.Mapping):
            return self._subsection(section_name=key, dictionary=value)
        else:
            value = self._evaluate(value)
            self._check_option(key=key, value=value)
            return value

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("invalid key {!r} of non-string type {}".format(key, type(key).__name__))
        elif not is_valid_identifier(key):
            raise ValueError("invalid key {!r}: malformed identifier".format(key))
        if isinstance(value, collections.Mapping):
            if self.has_option(key):
                raise TypeError("option {} cannot be replaced with a section".format(key))
            self.dictionary[key] = self._dictionary_factory()
            section = self._subsection(section_name=key, dictionary=self.dictionary[key])
            section.update(value)
        else:
            if self.has_section(key):
                raise TypeError("section {} cannot be replaced with an option".format(key))
            if not isinstance(value, Deferred):
                self._check_option(key=key, value=value)
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
        return self._subsection_class()(dictionary=self.dictionary.copy())

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def get_option(self, option_name, default=None):
        """get_option(self, option_name, default=None) -> value
           Get an option (raises KeyError if a section is found)
        """
        value = self.get(option_name, default)
        if isinstance(value, collections.Mapping):
            raise KeyError("{} is a section, not an option".format(option_name))
        return value

    def get_section(self, section_name, default=None):
        """get_section(self, section_name, default=None) -> value
           Get a section (raises KeyError if an option is found)
        """
        value = self.get(section_name, default)
        if not isinstance(value, collections.Mapping):
            raise KeyError("{} is an option, not a section".format(section_name))
        return value

    def __contains__(self, key):
        """__contains__(self, key) -> bool
           Return True if option or section 'key' exists.
        """
        return key in self.dictionary

    def has_key(self, key):
        """has_key(self, key) -> bool
           Return True if option or section exists.
        """
        return key in self

    def has_option(self, option_name):
        """has_option(self, option_name) -> bool
           Return True if option exists.
        """
        return option_name in self.dictionary and \
            not isinstance(self.dictionary[option_name], collections.Mapping)

    def has_section(self, section_name):
        """has_section(self, section_name) -> bool
           Return True if section exists.
        """
        return section_name in self.dictionary and \
            isinstance(self.dictionary[section_name], collections.Mapping)

    def add_section(self, section_name):
        """add_section(self, section_name) -> new section
           Add a new section and return it.
        """
        self[section_name] = {}
        return self[section_name]

    def options(self):
        """options(self) -> option items
           Iterator over option items
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
                value = self._subsection(section_name=key, dictionary=value)
            yield key, value

    def keys(self):
        for key, _ in self.items():
            yield key

    def values(self):
        for _, value in self.items():
            yield value

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

    def as_dict(self, *, dict_class=collections.OrderedDict, defaults=True, evaluate=True, ref_section=None):
        """as_dict(self, *, dict_class=collections.OrderedDict, defaults=True, evaluate=True, ref_section=None) -> dict
           Return a dict with all the section content
        """
        result = dict_class()
        subsection_class = self._subsection_class()
        for key, value in self.items():
            if isinstance(value, subsection_class):
                result[key] = value.as_dict(dict_class=dict_class, defaults=defaults,
                                            evaluate=evaluate, ref_section=ref_section)
            else:
                if evaluate:
                    value = self._evaluate(value, ref_section=ref_section)
                result[key] = value
        return result

    def __repr__(self):
        return "{}(dictionary={!r})".format(self.__class__.__name__, self.dictionary)

    def __str__(self):
        section_data = []
        subsection_class = self._subsection_class()
        for key, value in self.items():
            if isinstance(value, subsection_class):
                section_data.append((key, str(value)))
            else:
                section_data.append((key, repr(value)))
        content = ', '.join("{}={}".format(k, v) for k, v in section_data)
        return "{}({})".format(self.__class__.__name__, content)

    def __eq__(self, section):
        if isinstance(section, Section):
            return self.as_dict(dict_class=dict) == section.as_dict(dict_class=dict)
        else:
            return self.as_dict(dict_class=dict) == as_dict(section, depth=-1, dict_class=dict)

    def __bool__(self):
        for _ in self.items():
            return True
        return False

    def dump(self, stream=None, protocol="daikon", *, defaults=False):
        """dump(self, stream=None, protocol="daikon", defaults=False)
           Dump the content to a stream.
        """
        if stream is None:
            stream = sys.stdout
        serializer = Serializer.get_class(protocol)()
        obj = self.as_dict(defaults=defaults, evaluate=False)
        serializer.to_stream(stream=stream, obj=obj)


def iter_section_options(section):
    """iter_section_options(section)
       Iterates recursively on all option items.
    """
    sections = [((), section)]
    while sections:
        next_sections = []
        for rootname, section in sections:
            for o_name, o_value in section.options():
                yield rootname, o_name, o_value
            for s_name, s_value in section.sections():
                s_rootname = rootname + (s_name,)
                next_sections.append((s_rootname, s_value))
        sections = next_sections


def count_section_options(section):
    """count_section_options(section)
       Count number of options.
    """
    return sum(1 for _ in iter_section_options(section))


def has_section_options(section):
    """has_section_options(section)
       Return True if section has at least 1 option.
    """
    for _ in iter_section_options(section):
        return True
    return False
