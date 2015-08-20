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
Implementation of the Section class.

>>> section = Section()
>>> section["x_value"] = 10.1
>>> section["y_value"] = 20.2
>>> section["data"] = {"alpha": 20}
>>> section["data"]["name"] = "first experiment"
>>> section["z_value"] = 30.3
>>> section["velocity"] = {}
>>> section["velocity"]["filename"] = "vel.dat"
>>> section["velocity"]["type"] = "RAW"
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

__author__ = "Simone Campagna"
__all__ = [
    'Section',
    'iter_section_options',
    'count_section_options',
    'has_section_options',
    'get_section_value',
]

import collections
import collections.abc
import sys

from .toolbox.deferred import Deferred
from .toolbox.dictutils import as_dict
from .toolbox.identifier import is_valid_identifier
from .toolbox.serializer import Serializer


class Section(collections.abc.Mapping):
    """Dictionary-like object implementing storage of options/sections. The
       internal representation is stored onto a standard dictionary, which can
       be provided in construction.

       Parameters
       ----------
       init: Mapping, optional
           some initial content
       dictionary: Mapping, optional
           the internal dictionary
       parent: Section, optional
           the parent section
       name: str, optional
           the Section name
       interpolation: bool, optional
           enables interpolation
    """
    SUPPORTED_SEQUENCE_TYPES = (list, tuple)
    SUPPORTED_SCALAR_TYPES = (int, float, bool, str, type(None))

    def __init__(self, init=None, *, dictionary=None, parent=None, name=None, interpolation=True):
        self.interpolation = interpolation
        if dictionary is None:
            dictionary = self._dictionary_factory()
        self.dictionary = dictionary
        if parent is None:
            self.parent = self
            self.root = self
            self.fqname = ()
        else:
            self.parent = parent
            self.root = self.parent.root
            self.fqname = self.parent.fqname + (name,)
        # the reference root for ROOT and SECTION:
        if init:
            self.update(init)

    @classmethod
    def _subsection_class(cls):
        """Returns the class to be used for subsections (it must be derived from Section)

           Returns
           -------
           type
               the class to be used for subsections
        """
        return Section

    def _subsection(self, section_name, dictionary):
        """Returns a subsection with the given name

           Returns
           -------
           subsection_class
               a subsection_class instance
        """
        return self._subsection_class()(dictionary=dictionary, parent=self,
                                        interpolation=self.interpolation,
                                        name=section_name)

    @classmethod
    def _dictionary_factory(cls):
        """Factory for new dictionaries.

           Returns
           -------
           Mapping
               a dictionary
        """
        return collections.OrderedDict()

    def get_reference_root(self):
        """Returns the reference_root to be used for evaluation of deferred expressions.

           Returns
           -------
           Section
               the reference_root
        """
        return self.root

    def evaluate_option_value(self, value):
        """Evaluates an option's value.

           Parameters
           ----------
           value: any
               the option value

           Returns
           -------
           any
               the evaluated value
        """
        if isinstance(value, Deferred):
            if self.interpolation:
                reference_root = self.get_reference_root()
                section_getter = lambda: get_section_value(reference_root, *self.fqname)
                value = value.evaluate({'SECTION': section_getter, 'ROOT': reference_root})
            else:
                raise ValueError("cannot evaluate {}: interpolation is not enabled".format(
                    value.unparse()))
        return value

    def _check_option(self, key, value):
        """Checks the option type. Raises in case of errors.

           Parameters
           ----------
           key: str
               the key
           value: any
               the value
        """
        if isinstance(value, self.SUPPORTED_SCALAR_TYPES):
            pass
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
            value = self.evaluate_option_value(value)
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
            if isinstance(value, Deferred):
                if not self.interpolation:
                    raise ValueError("cannot set {}={}: interpolation is not enabled".format(
                        key, value.unparse()))
            else:
                self._check_option(key=key, value=value)
            self.dictionary[key] = value

    def __delitem__(self, key):
        del self.dictionary[key]

    def clear(self):
        """Clears all the section's content.
        """
        self.dictionary.clear()

    def copy(self):
        """Returns a deep copy of the section.
        """
        return self._subsection_class()(dictionary=self.dictionary.copy())

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def get_option(self, option_name, default=None):
        """Returns an option (raises KeyError if a section is found)

           Parameters
           ----------
           option_name: str
               the option name
           default: any
               the value to be used as default

           Returns
           -------
           any
               the option value, or None
        """
        value = self.get(option_name, default)
        if isinstance(value, collections.Mapping):
            raise KeyError("{} is a section, not an option".format(option_name))
        return value

    def get_section(self, section_name, default=None):
        """Returns a section (raises KeyError if an option is found)

           Parameters
           ----------
           section_name: str
               the section name
           default: any
               the value to be used as default

           Returns
           -------
           any
               the section, or None
        """
        value = self.get(section_name, default)
        if not isinstance(value, collections.Mapping):
            raise KeyError("{} is an option, not a section".format(section_name))
        return value

    def __contains__(self, key):
        return key in self.dictionary

    def has_key(self, key):
        """Returns True if option or section exists.

           Parameters
           ----------
           key: str
               the key

           Returns
           -------
           bool
               True if key exists
        """
        return key in self

    def has_option(self, option_name):
        """Returns True if option exists.

           Parameters
           ----------
           option_name: str
               the option name

           Returns
           -------
           bool
               True if option exists
        """
        return option_name in self.dictionary and \
            not isinstance(self.dictionary[option_name], collections.Mapping)

    def has_section(self, section_name):
        """Returns True if section exists.

           Parameters
           ----------
           section_name: str
               the section name

           Returns
           -------
           bool
               True if section exists
        """
        return section_name in self.dictionary and \
            isinstance(self.dictionary[section_name], collections.Mapping)

    def add_section(self, section_name):
        """Adds a new section and return it.
           Parameters
           ----------
           section_name: str
               the section name

           Returns
           -------
           section
               the new section
        """
        self[section_name] = {}
        return self[section_name]

    def options(self):
        """Iterator over option items.

           Returns
           -------
           iterator
               iterator over (option_name, option_value)
        """
        for key, value in self.items():
            if not isinstance(value, collections.Mapping):
                yield key, value

    def sections(self):
        """Iterator over section items.

           Returns
           -------
           iterator
               iterator over (section_name, section_value)
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
        """Updates with the content of the 'dictionary'

           Parameters
           ----------
           dictionary: Mapping
               the dictionary
        """
        for key, value in dictionary.items():
            self[key] = value

    def as_dict(self, *, dict_class=collections.OrderedDict, defaults=True, evaluate=True):
        """Returns a dict copy of all the section content.

           Parameters
           ----------
           dict_class: type, optional
               the dict class to be used to create dictionaries
           defaults: bool, optional
               if True copy also default values
           evaluate: bool, optional
               if True evaluate deferred expressions
        """
        result = dict_class()
        subsection_class = self._subsection_class()
        for key, value in self.items():
            if isinstance(value, subsection_class):
                result[key] = value.as_dict(dict_class=dict_class, defaults=defaults,
                                            evaluate=evaluate)
            else:
                if evaluate:
                    value = self.evaluate_option_value(value)
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

    def dump(self, stream=None, protocol="zirkon", *, defaults=False):
        """Dumps the content to a stream.

           Parameters
           ----------
           stream: file, optional
               the stream where to write (defaults to sys.stdout)
           protocol: str, optional
               the protocol (defaults to "zirkon")
           defaults: bool, optional
               if True, dump defaults too
        """
        if stream is None:
            stream = sys.stdout
        serializer = Serializer.get_class(protocol)()
        obj = self.as_dict(defaults=defaults, evaluate=False)
        serializer.to_stream(stream=stream, obj=obj)


def iter_section_options(section):
    """Iterates recursively on all option items.

       Parameters
       ----------
       section: Section
           a section object

       Returns
       -------
       iterator
           iterator over (rootname, option_name, option_value)
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
    """Counts the number of options.

       Parameters
       ----------
       section: Section
           a section object

       Returns
       -------
       int
           the number of options
    """
    return sum(1 for _ in iter_section_options(section))


def has_section_options(section):
    """Returns True if section has at least 1 option.

       Parameters
       ----------
       section: Section
           a section object

       Returns
       -------
       bool
           True if at least one option is found
    """
    for _ in iter_section_options(section):
        return True
    return False


def get_section_value(config, *keys):
    r"""Returns the value for a tuple of keys.
        get_section_value(config, k0, k1, k2) is equivalent to
        config[k0][k1][k2]

        Parameters
        ----------
        config: Section
            the config object
        \*keys: tuple
            the keys for successive gets

        Returns
        -------
        any
            the value
    """
    result = config
    for key in keys:
        result = result[key]
    return result
