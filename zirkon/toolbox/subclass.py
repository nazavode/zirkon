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
The subclass module contains functions to find all subclasses of
a given class (indirect subclasses too).
"""

__author__ = "Simone Campagna"
__all__ = [
    'subclasses',
    'find_subclass',
]


def subclasses(class_, *, include_self=False, filter=None):  # pylint: disable=W0622
    """subclasses(class_, *, include_self=False, filter=lambda : True) -> iterator
       Iterator over subclasses; class_ is included only if 'include_self' is True.
       Filter can be used, for instance, to exclude abstract classes.
    """
    if include_self:
        if filter is None or filter(class_):
            yield class_
    for subclass in class_.__subclasses__():  # pylint: disable=E1101
        yield from subclasses(subclass, include_self=True, filter=filter)


def find_subclass(class_, class_name, *, include_self=False, filter=None):  # pylint: disable=W0622
    """find_subclass(class_, class_name, *, include_self=False, filter=lambda : True) -> iterator
       Find a subclass of 'class_' whose name is 'class_name'. Return the found class, or None.
    """
    for subclass in subclasses(class_=class_, include_self=include_self, filter=filter):  # pylint: disable=W0622
        if subclass.__name__ == class_name:
            return subclass
    return None
