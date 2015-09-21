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
Implementation of the abstract Serializer class.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'Serializer',
]

import abc

from ..files import createdir
from ..registry import Registry

from .codec_catalog import CodecCatalog


class Serializer(Registry, metaclass=abc.ABCMeta):
    """Abstract base class for serializers. Serializers must implement
       to_string(obj) and from_string(serialization).
    """
    CODEC_CATALOG = CodecCatalog()

    @classmethod
    def codec_catalog(cls):
        """Returns the codec's catalog.

           Returns
           -------
           CodecCatalog
               the codec's catalog
        """
        return cls.CODEC_CATALOG

    @classmethod
    def is_binary(cls):
        """Returns True if the serialization is binary.

           Returns
           -------
           bool
               True if serialization is binary
        """
        return False

    @abc.abstractmethod
    def to_string(self, obj):
        """Returns the string serialization for 'obj'.

           Parameters
           ----------
           obj: |any|
               the object to be serialized

           Returns
           -------
           str
               the obj's serialization
        """
        raise NotImplementedError

    def to_stream(self, obj, stream):
        """Writes the serialization for 'obj' to file 'stream'.

           Parameters
           ----------
           obj: |any|
               the object to be serialized
           stream: file
               an open file

           Returns
           -------
           int
               the number of written bytes
        """
        return stream.write(self.to_string(obj))

    def to_file(self, obj, filename):
        """Writes the serialization for 'obj' to file 'filename'.

           Parameters
           ----------
           obj: |any|
               the object to be serialized
           filename: str
               the file name

           Returns
           -------
           int
               the number of written bytes
        """
        createdir(filename)
        mode = 'w'
        if self.is_binary():
            mode += 'b'
        with open(filename, mode) as f_stream:
            return self.to_stream(obj, f_stream)

    @abc.abstractmethod
    def from_string(self, serialization, *, filename=None):
        """Loads an object from string 'serialization'.

           Parameters
           ----------
           serialziation: str
               the serialization
           filename: str, optional
               the file name (only for error traceback)

           Returns
           -------
           |any|
               the deserialized object
        """
        raise NotImplementedError

    def from_stream(self, stream, *, filename=None):
        """Loads an object from open file 'stream'.

           Parameters
           ----------
           stream: file
               an open file
           filename: str, optional
               the file name (only for error traceback)

           Returns
           -------
           |any|
               the deserialized object
        """
        if filename is None:
            if hasattr(stream, 'name'):
                filename = stream.name
            else:
                filename = repr(stream)
        return self.from_string(serialization=stream.read(),
                                filename=filename)

    def from_file(self, filename):
        """Loads an object from file 'filename'.

           Parameters
           ----------
           file: str
               the file name

           Returns
           -------
           |any|
               the deserialized object
        """
        createdir(filename)
        mode = 'r'
        if self.is_binary():
            mode += 'b'
        with open(filename, mode) as f_stream:
            return self.from_stream(stream=f_stream,
                                    filename=filename)
