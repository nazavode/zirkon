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
config.config
=============
"""

__author__ = "Simone Campagna"

import collections

from .section import Section

from .toolbox.serializer import Serializer


class Config(Section):
    """Config(init=None, *, dictionary=None)
       Config class.

       >>> config = Config()
       >>> config['x_value'] = 10.1
       >>> config['y_value'] = 20.2
       >>> config['parameters'] = collections.OrderedDict((
       ...     ('alpha', 20),
       ...     ('name', 'first experiment'),
       ... ))
       >>> config['z_value'] = 30.3
       >>> config['velocity'] = collections.OrderedDict((
       ...     ('filename', 'vel.dat'),
       ...     ('type', 'RAW'),
       ... ))
       >>> config.dump()
       x_value = 10.1
       y_value = 20.2
       [parameters]
           alpha = 20
           name = 'first experiment'
       z_value = 30.3
       [velocity]
           filename = 'vel.dat'
           type = 'RAW'
       >>> del config['parameters']
       >>> config.dump()
       x_value = 10.1
       y_value = 20.2
       z_value = 30.3
       [velocity]
           filename = 'vel.dat'
           type = 'RAW'
       >>>
    """


    def __init__(self, init=None, *, dictionary=None):
        super().__init__(dictionary=dictionary, init=init)

    @classmethod
    def get_serializer(cls, protocol):
        """get_serializer(protocol)
           Return a serializer for the required protocol.
        """
        serializer_class = Serializer.get_class(protocol)
        if serializer_class is None:
            raise ValueError("serialization protocol {} not available [{}]".format(
                protocol,
                '|'.join(registered_class.class_tag() for registered_class in Serializer.classes()),
            ))
        return serializer_class()

    def to_string(self, protocol):
        """to_string(protocol)
           Serialize to stream 'stream' according to 'protocol'.
        """
        serializer = self.get_serializer(protocol)
        return serializer.to_string(self)

    def to_stream(self, stream, protocol):
        """to_stream(stream, protocol)
           Serialize to stream 'stream' according to 'protocol'.
        """
        serializer = self.get_serializer(protocol)
        return serializer.to_stream(self, stream)

    def to_file(self, filename, protocol):
        """to_file(filename, protocol)
           Serialize to file 'filename' according to 'protocol'.
        """
        serializer = self.get_serializer(protocol)
        return serializer.to_file(self, filename)

    @classmethod
    def from_file(cls, filename, protocol, *, dictionary=None):
        """from_file(filename, protocol, *, dictionary=None)
           Deserialize from file 'filename' according to 'protocol'.
        """
        serializer = cls.get_serializer(protocol)
        return serializer.from_file(cls, filename, dictionary=dictionary)

    @classmethod
    def from_stream(cls, stream, protocol, *, dictionary=None, filename=None):
        """from_stream(stream, protocol, *, dictionary=None, filename=None)
           Deserialize from stream 'stream' according to 'protocol'.
        """
        serializer = cls.get_serializer(protocol)
        return serializer.from_stream(cls, stream, dictionary=dictionary, filename=filename)

    @classmethod
    def from_string(cls, string, protocol, *, dictionary=None, filename=None):
        """from_string(string, protocol, *, dictionary=None, filename=None)
           Deserialize from string 'string' according to 'protocol'.
        """
        serializer = cls.get_serializer(protocol)
        return serializer.from_string(cls, string, dictionary=dictionary, filename=filename)

    def read(self, filename, protocol):
        """read(filename, protocol)
           Read from file 'filename' according to 'protocol'.
        """
        self.clear()
        self.from_file(filename=filename, protocol=protocol, dictionary=self.dictionary)

    def write(self, filename, protocol):
        """write(filename, protocol)
           Write to file 'filename' according to 'protocol'.
        """
        self.to_file(filename, protocol)
