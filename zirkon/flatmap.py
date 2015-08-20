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
Implementation of the FlatMap class. This class implements a nested dictionary
interface over a flat dictionary.
"""

__author__ = "Simone Campagna"

import collections
import collections.abc

from .toolbox.identifier import is_valid_identifier


class FlatMap(collections.abc.Mapping):
    """FlatMap implements a standard mapping using a flattened internal
       representation. The internal storage is provided by a standard dictionary
       (dict, OrderedDict).

       >>> flatmap = FlatMap(collections.OrderedDict())
       >>> flatmap['a'] = 10
       >>> flatmap['sub'] = {}
       >>> flatmap['sub']['x'] = 1
       >>> flatmap['sub']['y'] = 2
       >>> flatmap['b'] = 20
       >>> flatmap['c'] = 30
       >>> print(flatmap)
       FlatMap(a=10, sub=FlatMap(x=1, y=2), b=20, c=30)
       >>> del flatmap['b']
       >>> print(flatmap)
       FlatMap(a=10, sub=FlatMap(x=1, y=2), c=30)
       >>> del flatmap['sub']
       >>> print(flatmap)
       FlatMap(a=10, c=30)
       >>>

       Parameters
       ----------
       dictionary: Mapping, optional
           the internal dictionary
       init: Mapping, optional
           some initialization content
       prefix: str, optional
           an initial prefix for keys

    """
    DOT = '.'
    SUBMAP_PLACEHOLDER = None

    def __init__(self, dictionary, *, init=None, prefix=''):
        if dictionary is None:
            dictionary = self.dictionary_factory()
        self.dictionary = dictionary
        self.prefix = prefix
        if init:
            self.update(init)

    @classmethod
    def dictionary_factory(cls):
        """Factory for new dictionaries.
        """
        return collections.OrderedDict()

    def get_abs_key(self, rel_key, check=True):
        """Returns an absolute key name

           Parameters
           ----------
           rel_key: str
               the relative key
           check: bool, optional
               if True, runs check_rel_key(rel_key)

           Returns
           -------
           str
               the absolute key
        """
        if check:
            self.check_rel_key(rel_key)
        return self.prefix + rel_key

    def check_rel_key(self, rel_key):
        """Checks if 'rel_key' is correctly formed (== a valid python identifier). Raises in case on errors.

           Parameters
           ----------
           rel_key: str
               the relative key
        """
        if not isinstance(rel_key, str):
            raise TypeError("invalid key {}{} of type {}: {} keys must be strings".format(
                self.prefix,
                rel_key,
                type(rel_key).__name__,
                type(self).__name__,
            ))
        if self.DOT in rel_key:
            raise ValueError("invalid key {}{}: cannot contain {!r}".format(
                self.prefix,
                rel_key,
                self.DOT,
            ))
        if not is_valid_identifier(rel_key):
            raise ValueError("invalid key {}{}: invalid format".format(
                self.prefix,
                rel_key,
            ))

    def get_submap_prefix(self, abs_key):
        """Returns the submap prefix for a given absolute key.

           Parameters
           ----------
           abs_key: str
               the absolute key

           Returns
           -------
           str
               the submap prefix
        """
        return abs_key + self.DOT

    def nesting_level(self, rel_key):
        """Returns the nesting_level for a key.

           Parameters
           ----------
           rel_key: str
               the relative key

           Returns
           -------
           int
               the nesting level
        """
        level = rel_key.count(self.DOT)
        if rel_key.endswith(self.DOT):
            level -= 1
        return level

    def get_submap_name(self, rel_key):
        """Returns the submap name for a given relative key, or None is this is not a submap placeholder.
           Parameters
           ----------
           rel_key: str
               the relative key

           Returns
           -------
           str
               the submap name
        """
        if rel_key.endswith(self.DOT):
            return rel_key[:-1]
        else:
            return None

    def _iter_keys(self):
        """Iterates over (abs_key, rel_key)
        """
        for abs_key in self.dictionary.keys():
            if abs_key.startswith(self.prefix):
                rel_key = abs_key[len(self.prefix):]
                if rel_key:
                    yield abs_key, rel_key

    @classmethod
    def submap_class(cls):
        """Returns the class to be used for submaps.

           Returns
           -------
           type
               the submap FlatMap class
        """
        return FlatMap

    def submap(self, prefix):
        """Return a submap with a given prefix.

           Parameters
           ----------
           prefix: str
               the prefix

           Returns
           -------
           FlatMap
               the submap instance
        """
        return self.submap_class()(dictionary=self.dictionary, prefix=prefix)

    def __getitem__(self, key):
        abs_key = self.get_abs_key(key)
        if abs_key in self.dictionary:
            return self.dictionary[abs_key]
        else:
            submap_prefix = self.get_submap_prefix(abs_key)
            if submap_prefix in self.dictionary:
                return self.submap(prefix=submap_prefix)
        raise KeyError("undefined key {}{}".format(self.prefix, key))

    def __setitem__(self, key, value):
        abs_key = self.get_abs_key(key)
        submap_prefix = self.get_submap_prefix(abs_key)
        if isinstance(value, collections.Mapping):
            if abs_key in self.dictionary:
                raise ValueError("cannot replace key {}{} with submap".format(self.prefix, key))
            if submap_prefix in self.dictionary:
                # clear all submap's keys
                self[key].clear()
            submap = self.submap(prefix=submap_prefix)
            self.dictionary[submap_prefix] = self.SUBMAP_PLACEHOLDER
            for sub_key, sub_value in value.items():
                submap[sub_key] = sub_value
        else:
            if submap_prefix in self.dictionary:
                raise ValueError("cannot replace submap {}{} with key".format(self.prefix, key))
            self.dictionary[abs_key] = value

    def __delitem__(self, key):
        abs_key = self.get_abs_key(key)
        if abs_key in self.dictionary:
            del self.dictionary[abs_key]
            return
        submap_prefix = self.get_submap_prefix(abs_key)
        if submap_prefix in self.dictionary:
            submap = self[key]
            submap.clear()
            del self.dictionary[submap.prefix]
            return
        raise KeyError(self.prefix + key, "missing key/submap{}{}".format(self.prefix, key))

    def has_key(self, key):
        """Returns True if key/submap named 'key' is found.

           Parameters
           ----------
           key: str
               the key

           Returns
           -------
           bool
               True if key is in the flatmap
        """
        abs_key = self.get_abs_key(key)
        if abs_key in self.dictionary:
            return True
        submap_prefix = self.get_submap_prefix(abs_key)
        if submap_prefix in self.dictionary:
            return True
        return False

    def clear(self):
        """Clears all the dictionary content.
        """
        for abs_key, _ in self._iter_keys():
            if len(abs_key) > len(self.prefix):
                del self.dictionary[abs_key]

    def get(self, key, default=None):
        abs_key = self.get_abs_key(key)
        if abs_key in self.dictionary:
            return self.dictionary[abs_key]
        else:
            submap_prefix = self.get_submap_prefix(abs_key)
            if submap_prefix in self.dictionary:
                return self.submap(prefix=submap_prefix)
        return default

    def __contains__(self, key):
        abs_key = self.get_abs_key(key)
        return abs_key in self.dictionary or self.get_submap_prefix(abs_key) in self.dictionary

    def __len__(self):
        count = 0
        for _, rel_key in self._iter_keys():
            if self.nesting_level(rel_key) == 0:
                count += 1
        return count

    def items(self):
        for abs_key, rel_key in self._iter_keys():
            if self.nesting_level(rel_key) == 0:
                submap_name = self.get_submap_name(rel_key)
                if submap_name is not None:
                    yield submap_name, self.submap(prefix=abs_key)
                else:
                    yield rel_key, self.dictionary[abs_key]

    def keys(self):
        for rel_key, _ in self.items():
            yield rel_key

    def __iter__(self):
        for rel_key, _ in self.items():
            yield rel_key

    def values(self):
        for _, value in self.items():
            yield value

    def copy(self):
        """Returns a deep copy of the FlatMap instance.
        """
        if hasattr(self.dictionary, 'copy'):
            return self.__class__(dictionary=self.dictionary.copy())
        else:
            return self.__class__(self.dictionary_factory(), init=self.dictionary)

    def as_dict(self, *, dict_class=collections.OrderedDict):
        """Returns a dict with all the flatmap's content

           Parameters
           ----------
           dict_class: type, optional
               the class to be used to create dictionaries

           Returns
           -------
           dict_class
               the dictionary
        """
        result = dict_class()
        submap_class = self.submap_class()
        for rel_key, value in self.items():
            if isinstance(value, submap_class):
                result[rel_key] = value.as_dict(dict_class=dict_class)
            else:
                result[rel_key] = value
        return result

    def update(self, dictionary):
        """Updates with the content of the 'dictionary'.

           Parameters
           ----------
           dictionary: Mapping
               the dictionary
        """
        for key, value in dictionary.items():
            self[key] = value

    def __repr__(self):
        return "{}(dictionary={!r}, prefix={!r})".format(self.__class__.__name__, self.dictionary, self.prefix)

    def __str__(self):
        map_data = []
        submap_class = self.submap_class()
        for key, value in self.items():
            if isinstance(value, submap_class):
                map_data.append((key, str(value)))
            else:
                map_data.append((key, repr(value)))
        content = ', '.join("{}={}".format(k, v) for k, v in map_data)
        return "{}({})".format(self.__class__.__name__, content)

    def __eq__(self, dictionary):
        submap_class = self.submap_class()
        if isinstance(dictionary, submap_class) and dictionary.dictionary is self.dictionary:
            return dictionary.prefix == self.prefix
        else:
            # compare self vs dictionary
            for s_key, s_value in self.items():
                if s_key not in dictionary:
                    return False
                if s_value != dictionary[s_key]:
                    return False
            # compare dictionary vs self
            for d_key, d_value in dictionary.items():
                if d_key not in self:
                    return False
                if self[d_key] != d_value:
                    return False
            return True

    def __bool__(self):
        for _ in self._iter_keys():
            return True
        return False
