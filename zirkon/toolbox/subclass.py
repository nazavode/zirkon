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


def subclasses(class_type, *, include_self=False, filter=None):  # pylint: disable=W0622
    """Iterates over subclasses; class_type is included only if 'include_self' is True.
       Filter can be used, for instance, to exclude abstract classes.

       Parameters
       ----------
       class_type: type
           the base class
       include_self: bool, optional
           if True, includes class_type itself
       include_abstract: bool, optional
           if True, includes also "abstract" classes

       Yields
       ------
       type
           the found subclasses
    """
    if include_self:
        if filter is None or filter(class_type):
            yield class_type
    for subclass in class_type.__subclasses__():  # pylint: disable=E1101
        yield from subclasses(subclass, include_self=True, filter=filter)


def find_subclass(class_type, class_name, *, include_self=False, filter=None):  # pylint: disable=W0622
    """Finds a subclass of 'class_type' whose name is 'class_name'. Return the found class, or None.

       Parameters
       ----------
       class_type: type
           the base class
       include_self: bool, optional
           if True, includes class_type itself
       filter: callable, optional
           a filtering function

       Returns
       -------
       type
           the first found subclass or None
    """
    for subclass in subclasses(class_type=class_type, include_self=include_self,
                               filter=filter):  # pylint: disable=W0622
        if subclass.__name__ == class_name:
            return subclass
    return None
