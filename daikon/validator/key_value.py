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
config.validator.key_value
==========================
Implementation of the KeyValue class
"""

__author__ = "Simone Campagna"
__all__ = [
    'KeyValue',
]


class KeyValue(object):
    """KeyValue(key, value, *, defined=None)
       Key/value ocject.
    """
    def __init__(self, key, value, *, defined=None):
        self.key = key
        self.value = value
        self.defined = defined

    def is_defined(self):
        """is_defined()
           Returns defined attribute.
        """
        return self.defined

    def copy(self):
        """copy()
           Return a copy of the KeyValue object.
        """
        return self.__class__(key=self.key, value=self.value, defined=self.defined)

    def __repr__(self):
        return "{}(key={!r}, value={!r}, defined={!r})".format(
            self.__class__.__name__,
            self.key,
            self.value,
            self.defined)

    def __str__(self):
        if self.defined:
            vstring = repr(self.value)
        else:
            vstring = '<undefined>'
        return "{}={}".format(self.key, vstring)

