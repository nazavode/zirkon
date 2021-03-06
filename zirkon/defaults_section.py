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
Implementation of the DefaultsSection class, used to store defaults in Config.
The referencing() method is a context manager used to temporarily set the
reference root for the DefaultsSection object to the ConfigSection instance.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'DefaultsSection',
]

import contextlib

from .section import Section


class DefaultsSection(Section):
    """A Section to store defaults for ConfigSection.
       The reference_root attribute is used for evaluation of macros;
       it must be set through the 'referencing' context manager method:

       >>> from zirkon.macros import ROOT
       >>> from zirkon.section import Section
       >>> defaults = DefaultsSection({'x': ROOT['n'] + 2})
       >>> section1 = Section({'n': 10})
       >>> section2 = Section({'n': 30})
       >>> with defaults.referencing(section1):
       ...     print(defaults['x'])
       12
       >>> with defaults.referencing(section2):
       ...     print(defaults['x'])
       32

       Parameters
       ----------
       init: Mapping, optional
           some initial content
       dictionary: Mapping, optional
           the internal dictionary
       parent: Section, optional
           the parent Section
       name: str, optional
           the Section name
       macros: bool, optional
           enables macros
       reference_root: Section, optional
           the reference root
    """
    def __init__(self, init=None, *, dictionary=None, parent=None, name=None,
                 macros=True, reference_root=None):
        self._reference_root = reference_root
        super().__init__(init=init, dictionary=dictionary, parent=parent,
                         macros=macros, name=name)

    @property
    def reference_root(self):
        """Returns a reference to the internal reference_root attribute

        Returns
        -------
        |Section|
            the reference root section
        """
        return self._reference_root

    @classmethod
    def _subsection_class(cls):
        return DefaultsSection

    def _subsection(self, section_name, dictionary):
        return self._subsection_class()(dictionary=dictionary, parent=self,
                                        macros=self.macros,
                                        name=section_name, reference_root=self.get_reference_root())

    @contextlib.contextmanager
    def referencing(self, section):
        """Context manager to temporarily switch reference_root to section.

           Parameters
           ----------
           section: ConfigSection
               a section to be temporarily used as reference_root

           Yields
           ------
           self
               the defaults section itself
        """
        saved_reference_root = self._reference_root
        reference_root = section.get_reference_root()
        self._reference_root = reference_root
        yield self
        self._reference_root = saved_reference_root

    def get_reference_root(self):
        return self._reference_root
