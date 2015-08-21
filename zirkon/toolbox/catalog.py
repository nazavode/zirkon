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

"""\
Implementation of the Catalog class. This class registers information
about classes. It provides methods to find the best match for any class.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'Catalog',
]

import collections

from .subclass import subclasses


class Catalog(object):
    """Class catalog; stores information about classes, and provides methods
       to find the best matching class for a given object. The best match is the
       closest class which is a base class for the object.

       Parameters
       ----------
       default_factory: callable
           the function providing default values when a match cannot be found
           (defaults to 'lambda: None')

       Attributes
       ----------
       default_factory: callable
           the function providing default values when a match cannot be found
           (defaults to 'lambda: None')
       class_info: OrderedDict
           the class info dictionary
    """

    def __init__(self, default_factory=lambda: None):
        self.class_info = collections.OrderedDict()
        self._cache = {}
        self._name_cache = {}
        self.default_factory = default_factory

    def register(self, class_type, info):
        """Register a new class.

           Parameters
           ----------
           class_type: type
               the class to be registered
           info: any
               the information to be registered
        """
        self.class_info[class_type] = info

    def get(self, class_or_name, exact=False):
        """Returns registered info for a class or class name 'class_or_name'.

           Parameters
           ----------
           class_or_name: type/str
               the class (or class name) for which info is requested
           exact: bool
               if True, returns only exact matches

           Returns
           -------
           any
               the requested info, or None
        """
        if isinstance(class_or_name, str):
            return self.get_by_name(class_or_name, exact=exact)
        else:
            return self.get_by_class(class_or_name, exact=exact)

    def get_by_class(self, class_type, exact=False):
        """Returns registered info for a class 'class_type'.

           Parameters
           ----------
           class_type: type
               the class for which info is requested
           exact: bool
               if True, returns only exact matches

           Returns
           -------
           any
               the requested info, or None
        """
        if class_type in self.class_info:
            return self.class_info[class_type]
        else:
            if not exact:
                if class_type in self._cache:
                    best_distance, best_match = self._cache[class_type]
                else:
                    best_distance, best_match = self._get_best_match(class_type)
                    self._cache[class_type] = best_distance, best_match
                if best_distance is not None:
                    return self.class_info[best_match]
            return self.default_factory()

    def get_by_name(self, class_name, exact=False):
        """Returns info for a class named 'class_name'. If 'exact' returns only exact matches.

           Parameters
           ----------
           class_name: str
               the name of the class for which info is requested
           exact: bool
               if True, returns only exact matches

           Returns
           -------
           any
               the requested info, or None
        """
        for class_type, info in self.class_info.items():
            if class_type.__name__ == class_name:
                return info
        if exact:
            return self.default_factory()
        else:
            if class_name in self._name_cache:
                class_type = self._name_cache[class_name]
            else:
                class_type = self._get_subclass_by_name(class_name)
                self._name_cache[class_name] = class_type
            if class_type is None:
                return self.default_factory()
            else:
                return self.get_by_class(class_type, exact=exact)

    def _get_subclass_by_name(self, class_name):
        """Returns a registered subclass whose name is 'class_name'.

           Parameters
           ----------
           class_name: str
               the class name

           Returns
           -------
           type
               the requested class, or None if not found
        """
        for class_type in self.class_info.keys():
            for subclass in subclasses(class_type, include_self=False):
                if subclass.__name__ == class_name:
                    return subclass
        return None

    def _get_best_match(self, class_type):
        """Returns the closest class for a given class, based on __mro__ of registered
           classes.

           Parameters
           ----------
           class_type: type
               the class

           Returns
           -------
           distance, matching_class
               the distance and the matching class; if not found, distance is None.
        """
        best_match, best_distance = None, None
        for distance, base_class in enumerate(class_type.__mro__):
            for registered_class in self.class_info.keys():
                if base_class is registered_class:
                    if best_distance is None or best_distance > distance:
                        best_match, best_distance = registered_class, distance
                    break
        return best_distance, best_match
