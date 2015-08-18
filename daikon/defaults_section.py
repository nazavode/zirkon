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

from .section import Section


class DefaultsSection(Section):
    """DefaultsSection(...)
       A Section to store ValidationResult values.
    """
    def __init__(self, init=None, *, dictionary=None, parent=None, name=None, reference_root=None):
        self._reference_root = reference_root
        super().__init__(init=init, dictionary=dictionary, parent=parent, name=name)

    @classmethod
    def _subsection_class(cls):
        return DefaultsSection

    def _subsection(self, section_name, dictionary):
        return self._subsection_class()(dictionary=dictionary, parent=self,
                                        name=section_name, reference_root=self._get_reference_root())

    def _get_reference_root(self):
        # use always the root reference_root, which is correctly set
        return self.root._reference_root  # pylint: disable=W0212

    def set_reference_root(self, reference_root):
        """setup_reference_root(reference_root)"""
        if self._reference_root is None:
            self._reference_root = reference_root
        elif self._reference_root is not reference_root:
            raise ValueError("reference root already set - defaults cannot be shared")
