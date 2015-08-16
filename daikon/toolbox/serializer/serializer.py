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
config.toolbox.serializer.serializer
====================================
Implementation of the abstract serializer class
"""

__author__ = "Simone Campagna"

import abc

from ..files import createdir
from ..registry import Registry

from .codec_catalog import CodecCatalog


class Serializer(Registry, metaclass=abc.ABCMeta):
    """Serializer()
       Abstract base class for serializers. Serializers must implement
       to_string(obj) and from_string(serialization).
    """
    CODEC_CATALOG = CodecCatalog()

    @classmethod
    def codec_catalog(cls):
        """codec_catalog() -> class' codec catalog"""
        return cls.CODEC_CATALOG

    @classmethod
    def is_binary(cls):
        """is_binary() -> bool
           Return True if the serialization is binary.
        """
        return False

    @abc.abstractmethod
    def to_string(self, obj):
        """to_string(obj) -> str
           Dump the serialization for 'obj'.
        """
        raise NotImplementedError

    def to_stream(self, obj, stream):
        """to_stream(obj, stream)
           Write the serialization for 'obj' to stream 'stream'.
        """
        return stream.write(self.to_string(obj))

    def to_file(self, obj, filename):
        """to_file(obj, filename)
           Write the serialization for 'obj' to file 'filename'.
        """
        createdir(filename)
        mode = 'w'
        if self.is_binary():
            mode += 'b'
        with open(filename, mode) as f_stream:
            return self.to_stream(obj, f_stream)

    @abc.abstractmethod
    def from_string(self, serialization, *, filename=None):
        """from_string(serialization, *, filename=None) -> obj
           Load a Config from string 'serialization'.
        """
        raise NotImplementedError

    def from_stream(self, stream, *, filename=None):
        """from_stream(stream, *, filename=None) -> obj
           Load a Config from stream 'stream'.
        """
        if filename is None:
            if hasattr(stream, 'name'):
                filename = stream.name
            else:
                filename = repr(stream)
        return self.from_string(serialization=stream.read(),
                                filename=filename)

    def from_file(self, filename):
        """from_file(filename) -> obj
           Load a Config from file 'filename'.
        """
        createdir(filename)
        mode = 'r'
        if self.is_binary():
            mode += 'b'
        with open(filename, mode) as f_stream:
            return self.from_stream(stream=f_stream,
                                    filename=filename)
