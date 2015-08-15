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
    'ConfigSection',
]

from .section import Section, has_section_options


class ConfigSection(Section):
    """ConfigSection(...)
       Adds support for defaults.
    """
    SUPPORTED_SEQUENCE_TYPES = (list, tuple)
    SUPPORTED_SCALAR_TYPES = (int, float, bool, str, type(None))

    def __init__(self, init=None, *, dictionary=None, parent=None, defaults=True):
        if defaults is True:
            defaults = Section()
        elif defaults is False:
            defaults = None
        elif defaults is None or isinstance(defaults, Section):
            defaults = defaults
        else:
            raise TypeError("invalid defaults object of type {}: not a Section".format(
                type(defaults).__name__))
        self._defaults = defaults
        self._has_defaults = self._defaults is not None
        super().__init__(init=init, dictionary=dictionary, parent=parent)

    @classmethod
    def _subsection_class(cls):
        return ConfigSection

    def _subsection(self, section_name, dictionary):
        if self._has_defaults:
            if section_name in self._defaults:
                subdefaults = self._defaults[section_name]
            else:
                subdefaults = self._defaults.add_section(section_name)
        else:
            subdefaults=None
        return self._subsection_class()(dictionary=dictionary, parent=self, defaults=subdefaults)

    def add_defaults(self, **kwargs):
        """add_defaults(**kwargs)
           Add default options and sections"""
        if self._has_defaults:
            section = self._defaults
        else:
            section = self
        for option_name, option_value in kwargs.items():
            section[option_name] = option_value

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
                return self._defaults.has_section(section_name) and has_section_options(self._defaults[section_name])
            else:
                return False

    def has_key(self, key):
        if super().has_key(key):
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
        return self._subsection_class()(dictionary=self.dictionary.copy(),
                                        defaults=self._defaults.copy())

    def __getitem__(self, key):
        if super().has_key(key):
            return super().__getitem__(key)
        else:
            if self._has_defaults and key in self._defaults:
                return self._defaults[key]
            else:
                raise KeyError(key)
