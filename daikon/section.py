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
from .toolbox.deferred import Deferred
from .toolbox.undefined import UNDEFINED


class Section(collections.abc.Mapping):
    """Section(init=None, *, dictionary=None, parent=None, defaults=UNDEFINED)
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

    def __init__(self, init=None, *, dictionary=None, parent=None, defaults=UNDEFINED):
        if dictionary is None:
            dictionary = self._dictionary_factory()
        self.dictionary = dictionary
        if parent is None:
            self.parent = self
            self.root = self
        else:
            self.parent = parent
            self.root = self.parent.root
        if defaults is UNDEFINED:
            self._defaults = self._subsection_class()(defaults=None)
        else:
            self._defaults = defaults
        if init:
            self.update(init)

    @classmethod
    def _subsection_class(cls):
        """_subsection_class(cls)
           Return the class to be used for subsections (it must be derived from Section)
        """
        return Section

    def _subsection(self, section_name, dictionary=UNDEFINED):
        """_subsection(self, key, dictionary=UNDEFINED)
           Return a subsection named 'section_name' with dictionary 'dictionary'
        """
        if dictionary is UNDEFINED:
            dictionary = self.dictionary[section_name]
        if self._defaults is None:
            defaults = None
        else:
            if section_name in self._defaults:
                defaults = self._defaults[section_name]
            else:
                defaults = self._defaults.add_section(section_name)
        return self._subsection_class()(dictionary=dictionary, parent=self, defaults=defaults)

    @classmethod
    def _dictionary_factory(cls):
        """_dictionary_factory() -> new (empty) dictionary
           Factory for new dictionaries.
        """
        return collections.OrderedDict()

    def check_data_type(self, key, value):
        """check_data_type(key, value)
        """
        if isinstance(value, self.SUPPORTED_SCALAR_TYPES):
            return
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
            return
        else:
            raise TypeError("option {}: invalid value {!r} of type {}".format(
                key,
                value,
                type(value).__name__,
            ))

    def __getitem__(self, key):
        if key in self.dictionary:
            value = self.dictionary[key]
        elif self._defaults is not None and key in self._defaults:
            value = self._defaults[key]
        else:
            raise KeyError(key)
        if isinstance(value, collections.Mapping):
            return self._subsection(section_name=key, dictionary=value)
        else:
            self.check_data_type(key=key, value=value)
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
            if isinstance(value, Deferred):
                value = value.evaluate({'SECTION': self, 'ROOT': self.root})
            self.check_data_type(key=key, value=value)
            if self.has_section(key):
                raise TypeError("section {} cannot be replaced with an option".format(key))
            self.dictionary[key] = value

    def __delitem__(self, key):
        value = self.dictionary[key]
        if isinstance(value, collections.Mapping):
            if self._defaults is not None and key in self._defaults:
                del self._defaults[key]
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
        if option_name not in self.dictionary:
            if self._defaults is not None:
                return self._defaults.get(option_name, default)
            else:
                return default
        else:
            value = self.dictionary[option_name]
            if isinstance(value, collections.Mapping):
                raise KeyError("{} is a section, not an option".format(option_name))
            return value

    def get_section(self, section_name, default=None):
        """get_section(self, section_name, default=None) -> value
           Get a section (raises KeyError if an option is found)
        """
        if section_name not in self.dictionary:
            return default
        else:
            value = self.dictionary[section_name]
            if not isinstance(value, collections.Mapping):
                raise KeyError("{} is an option, not a section".format(section_name))
            value = self._subsection(section_name=section_name, dictionary=value)
            return value

    def has_key(self, key):
        """has_key(self, key) -> bool
           Return True if option or section 'key' exists.
        """
        return key in self.dictionary or (self._defaults is not None and key in self._defaults)

    def has_option(self, option_name):
        """has_option(self, option_name) -> bool
           Return True if option exists.
        """
        if option_name in self.dictionary and \
                not isinstance(self.dictionary[option_name], collections.Mapping):
            return True
        else:
            return self._defaults is not None and self._defaults.has_option(option_name)

    def has_section(self, section_name):
        """has_section(self, section_name) -> bool
           Return True if section exists.
        """
        if section_name in self.dictionary and \
                isinstance(self.dictionary[section_name], collections.Mapping):
            return True
        else:
            return self._defaults is not None and self._defaults.has_section(section_name)

    def add_default(self, **kwargs):
        """add_default(self, **kwargs)
           Add default options/sections.
        """
        for option_name, option_value in kwargs.items():
            self._defaults[option_name] = option_value

    def add_section(self, section_name):
        """add_section(self, section_name) -> new section
           Add a new section and return it.
        """
        self[section_name] = {}
        return self[section_name]

    def defaults(self):
        """defaults(self) -> default items
           Iterator over default option items.
        """
        if self._defaults is not None:
            for key, value in self._defaults.items():
                if key not in self.dictionary:
                    yield key, value

    def options(self, defaults=False):
        """options(self, defaults=False) -> option items
           Iterator over option items; if defaults, iterates also over defaults.
        """
        for key, value in self.items():
            if not isinstance(value, collections.Mapping):
                yield key, value
        if defaults:
            yield from self.defaults()

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

    def __contains__(self, key):
        return key in self.dictionary or (self._defaults is not None and key in self._defaults)

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
        if isinstance(dictionary, Section):
            dictionary_defaults = dictionary._defaults  # pylint: disable=W0212
            if self._defaults is not None and dictionary_defaults is not None:
                self._defaults.update(dictionary_defaults)

    def as_dict(self, *, dict_class=collections.OrderedDict, defaults=True):
        """as_dict(self, *, dict_class=collections.OrderedDict, defaults=True) -> dict
           Return a dict with all the section content
        """
        result = dict_class()
        subsection_class = self._subsection_class()
        for key, value in self.items():
            if isinstance(value, subsection_class):
                result[key] = value.as_dict(dict_class=dict_class)
            else:
                result[key] = value
        if defaults:
            for key, value in self.defaults():
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
            return compare_dicts(section.dictionary, self.dictionary)
        else:
            # coompare self vs section
            for key, value in self.items():
                if key not in section:
                    return False
                if value != section[key]:
                    return False
            # coompare section vs self
            for key, value in section.items():
                if key not in self:
                    return False
                if self[key] != value:
                    return False
            return True

    def __bool__(self):
        for _ in self.items():
            return True
        return False

    def dump(self, stream=None, protocol="daikon"):
        """dump(self, stream=None, protocol="daikon")
           Dump the content to a stream.
        """
        if stream is None:
            stream = sys.stdout
        serializer = Serializer.get_class(protocol)()
        serializer.to_stream(stream=stream, config=self)
