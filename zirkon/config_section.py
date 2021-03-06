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
Implementation of the ConfigSection class.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'ConfigSection',
]

import collections
import contextlib

from .section import Section, has_section_options
from .defaults_section import DefaultsSection


def _update_defaults(config, defaults):
    """Update config unset values with defaults.
    """
    for key, value in defaults.items():
        if isinstance(value, collections.Mapping):
            if config.has_section(key):
                section = config.get_section(key)
            else:
                section = config.add_section(key)
            _update_defaults(section, value)
        else:
            if not config.has_option(key):
                config[key] = value


class ConfigSection(Section):
    """Config section adding support for default values.

       Parameters
       ----------
       init: |Mapping|, optional
           some initial content
       dictionary: |Mapping|, optional
           the internal dictionary
       parent: |Section|, optional
           the parent section
       name: str, optional
           the section name
       macros: bool, optional
           enables macros
       defaults: bool, optional
           enables defaults
    """
    SUPPORTED_SEQUENCE_TYPES = (list, tuple)
    SUPPORTED_SCALAR_TYPES = (int, float, bool, str, type(None))

    def __init__(self, init=None, *, dictionary=None, parent=None, name=None,
                 defaults=True, macros=True):
        self._set_defaults(defaults)
        super().__init__(init=init, dictionary=dictionary, parent=parent,
                         name=name, macros=macros)

    def _set_defaults(self, value):
        """Set defaults attribute

           Parameters
           ----------
           value: |any|
               the defaults value to be set

           Raises
           ------
           TypeError
               invalid defaults object
        """
        if value is False or value is None:
            defaults = None
        elif isinstance(value, DefaultsSection):
            defaults = value
        elif value is True:
            defaults = DefaultsSection()
        elif isinstance(value, Section):
            defaults = DefaultsSection(dictionary=value.dictionary)
        elif isinstance(value, collections.Mapping):
            defaults = DefaultsSection(dictionary=value)
        else:
            raise TypeError("invalid defaults object of type {}: not a Section".format(
                type(value).__name__))
        self._defaults = defaults
        self._has_defaults = self._defaults is not None

    @property
    def defaults(self):
        """Returns the defaults value.

        Returns
        -------
        |DefaultsSection|
            the defaults section
        """
        return self._defaults

    @classmethod
    def _subsection_class(cls):
        return ConfigSection

    def _subsection(self, section_name, dictionary):
        if self._has_defaults:
            with self._defaults.referencing(self):
                if section_name in self._defaults:
                    subdefaults = self._defaults[section_name]
                else:
                    subdefaults = self._defaults.add_section(section_name)
        else:
            subdefaults = None
        return self._subsection_class()(dictionary=dictionary, parent=self,
                                        macros=self.macros,
                                        name=section_name, defaults=subdefaults)

    def set_defaults(self, **kwargs):
        r"""Set default options and sections

            Parameters
            ----------
            \*\*kwargs
                a list of key=value items
        """
        if self._has_defaults:
            for key, value in kwargs.items():
                self._defaults[key] = value
        else:
            _update_defaults(self, kwargs)

    def has_option(self, option_name):
        if super().has_option(option_name):
            return True
        else:
            if self._has_defaults:
                return self._defaults.has_option(option_name)
            else:
                return False

    def has_section(self, section_name):
        if super().has_section(section_name):
            return True
        else:
            if self._has_defaults:
                return self._defaults.has_section(section_name) and \
                    has_section_options(self._defaults[section_name])
            else:
                return False

    def __contains__(self, key):
        if super().__contains__(key):
            return True
        else:
            if self._has_defaults:
                if self._defaults.has_section(key):
                    return has_section_options(self._defaults[key])
                else:
                    return self._defaults.has_option(key)
            else:
                return False

    def copy(self):
        if self._has_defaults:
            defaults = self._defaults.copy()
        else:
            defaults = None
        return self._subsection_class()(dictionary=self.dictionary.copy(),
                                        defaults=defaults)

    def __getitem__(self, key):
        if super().__contains__(key):
            return super().__getitem__(key)
        else:
            if self._has_defaults and key in self._defaults:
                with self._defaults.referencing(self):
                    value = self._defaults[key]
                if isinstance(value, collections.Mapping):
                    if has_section_options(value):
                        return self.add_section(key)
                else:
                    return value
        raise KeyError(key)

    def __delitem__(self, key):
        if self._has_defaults and key in self._defaults:
            # ignore del error
            with contextlib.suppress(KeyError):
                super().__delitem__(key)
        else:
            super().__delitem__(key)

    def update(self, dictionary):
        super().update(dictionary)
        if isinstance(dictionary, ConfigSection):
            if self._has_defaults and dictionary.defaults is not None:
                with self._defaults.referencing(self):
                    self._defaults.update(dictionary.defaults)

    def as_dict(self, *, dict_class=collections.OrderedDict, defaults=True, evaluate=True):
        if defaults and self._has_defaults:
            with self._defaults.referencing(self):
                defaults_dict = self._defaults.as_dict(dict_class=dict_class,
                                                       evaluate=evaluate)
        else:
            defaults_dict = None
        self_dict = super().as_dict(dict_class=dict_class, defaults=defaults,
                                    evaluate=evaluate)
        if defaults_dict is None:
            return self_dict
        else:
            defaults_dict.update(self_dict)
            return defaults_dict

