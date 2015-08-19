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
daikon.defaults_section
=======================
Implementation of the DefaultsSection class
"""

__author__ = "Simone Campagna"
__all__ = [
    'DefaultsSection',
]

import contextlib

from .section import Section


class DefaultsSection(Section):
    """DefaultsSection(...)
       A Section to store defaults for ConfigSection.

       The reference_root attribute is used for evaluation of deferred expressions;
       it must be set through the 'referencing' context manager method:

       >>> from daikon.deferred_object import ROOT
       >>> defaults = DefaultsSection({'x': ROOT['n'] + 2})
       >>> section1 = Section({'n': 10})
       >>> section2 = Section({'n': 30})
       >>> with defaults.referencing(section1):
       ...     print(defaults['x'])
       12
       >>> with defaults.referencing(section2):
       ...     print(defaults['x'])
       32
    """
    def __init__(self, init=None, *, dictionary=None, parent=None, name=None,
                 interpolation=True, reference_root=None):
        self.reference_root = reference_root
        super().__init__(init=init, dictionary=dictionary, parent=parent,
                         interpolation=interpolation, name=name)

    @classmethod
    def _subsection_class(cls):
        return DefaultsSection

    def _subsection(self, section_name, dictionary):
        return self._subsection_class()(dictionary=dictionary, parent=self,
                                        interpolation=self.interpolation,
                                        name=section_name, reference_root=self.get_reference_root())

    @contextlib.contextmanager
    def referencing(self, section):
        """referencing(section)
           Context manager to temporarily switch reference_root
        """
        saved_reference_root = self.reference_root
        reference_root = section.get_reference_root()
        self.reference_root = reference_root
        yield self
        self.reference_root = saved_reference_root

    def get_reference_root(self):
        return self.reference_root
