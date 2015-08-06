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
config.serializer.class_archive
===============================
Implementation of the ClassRegistry registry. This class registers 
classes and related information. It implements methods to find the
best match for any class.
"""

__author__ = "Simone Campagna"
__all__ = [
    'ClassRegistry',
]

import collections

from .subclass import subclasses


class ClassRegistry(object):
    """ClassRegistry(default_factory=lambda : None)
       Registry for classes.
    """

    def __init__(self, default_factory=lambda : None):
        self.class_info = collections.OrderedDict()
        self._cache = {}
        self._name_cache = {}
        self.default_factory = default_factory


    def register(self, class_, info):
        """register(class_, info)
           Register a new class.
        """
        self.class_info[class_] = info

    def get(self, class_or_name, exact=False):
        """get_by_class(class_, exact=False) -> info
           Get info for a class 'class_'. If 'exact' returns only exact matches.
        """
        if isinstance(class_or_name, str):
            return self.get_by_name(class_or_name, exact=exact)
        else:
            return self.get_by_class(class_or_name, exact=exact)

    def get_by_class(self, class_, exact=False):
        """get_by_class(class_, exact=False) -> info
           Get info for a class 'class_'. If 'exact' returns only exact matches.
        """
        if class_ in self.class_info:
            return self.class_info[class_]
        else:
            if not exact:
                if class_ in self._cache:
                    best_distance, best_match = self._cache[class_]
                else:
                    best_distance, best_match = self._get_best_match(class_)
                    self._cache[class_] = best_distance, best_match
                if best_distance is not None:
                    return self.class_info[best_match]
            return self.default_factory()
            
    def get_by_name(self, class_name, exact=False):
        """get_by_name(class_name, exact=False) -> info
           Get info for a class named 'class_name'. If 'exact' returns only exact matches.
        """
        for class_, info in self.class_info.items():
            if class_.__name__ == class_name:
                return info
        if exact:
            return self.default_factory()
        else:
            if class_name in self._name_cache:
                class_ = self._name_cache[class_name]
                print("::: @1", class_name, class_, self._name_cache)
            else:
                class_ = self._get_subclass_by_name(class_name)
                print("::: @2", class_name, class_, self._name_cache)
                self._name_cache[class_name] = class_
            if class_ is None:
                return self.default_factory()
            else:
                return self.get_by_class(class_, exact=exact)
                        
        
    def _get_subclass_by_name(self, class_name):
        """_get_subclass_by_name(class_name) -> subclass or None
           Finds a subclass of any registered whose name is 'class_name'.
           If not found, it returns None.
        """
        for class_ in self.class_info.keys():
            for subclass in subclasses(class_, include_self=False):
                if class_name == 'FloatTuple':
                    print("::: @3 {!r} {!r} {!r}".format(class_name, class_.__name__, subclass.__name__))
                if subclass.__name__ == class_name:
                    return subclass
        return None
             
    def _get_best_match(self, class_):
        """_get_best_match(class_) -> best_distance, best_match_class
           Returns the best match for a given class, based on __mro__ of registered
           classes. If a match cannot be found, 'distance' is None.
        """
        best_match, best_distance = None, None
        for distance, base_class in enumerate(class_.__mro__):
            for registered_class in self.class_info.keys():
                if base_class is registered_class:
                    if best_distance is None or best_distance > distance:
                        best_match, best_distance = registered_class, distance
                    break
        return best_distance, best_match
