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

from .serializer import Serializer


class Config(Section):
    """Config(container=None)
       Given a flattened 'container' (by default, OrderedDict()), Config implements
       a nested subsection view on it.

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

    CONTAINER_FACTORY = collections.OrderedDict

    def __init__(self, init=None, *, container=None):
        if container is None:
            container = self.CONTAINER_FACTORY()
        super().__init__(container=container, prefix='', init=init)

    @classmethod
    def get_serializer(cls, protocol):
        """get_serializer(protocol)
           Return a serializer for the required protocol.
        """
        serializer_class = Serializer.get_plugin(protocol)
        if serializer_class is None:
            raise ValueError("serialization protocol {} not available [{}]".format(
                protocol,
                '|'.join(plugin_class.plugin_name() for plugin_class in Serializer.subclasses()),
            ))
        return serializer_class()

    def to_file(self, filename, protocol):
        """to_file(filename, protocol)
           Serialize to file 'filename' according to 'protocol'.
        """
        serializer = self.get_serializer(protocol)
        serializer.to_file(self, filename)

    @classmethod
    def from_file(cls, filename, protocol, *, container=None):
        """from_file(filename, protocol, *, container=None)
           Deserialize from file 'filename' according to 'protocol'.
        """
        serializer = cls.get_serializer(protocol)
        return serializer.from_file(cls, filename, container=container)
