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
daikon.config.config
====================
"""

__author__ = "Simone Campagna"
__all__ = [
    'Config',
    'ConfigValidationError',
    'SECTION',
    'ROOT',
]


from .config_base import ConfigBase, ConfigValidationError
from .config_section import ConfigSection
from .deferred_object import ROOT, SECTION


class Config(ConfigBase, ConfigSection):
    """Config(init=None, *, dictionary=None, defaults=True, schema=None, validate=True)
       Config class.

       >>> import collections
       >>> config = Config()
       >>> config['x_value'] = 10.1
       >>> config['y_value'] = 20.2
       >>> config['data'] = collections.OrderedDict((
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
       [data]
           alpha = 20
           name = 'first experiment'
       z_value = 30.3
       [velocity]
           filename = 'vel.dat'
           type = 'RAW'
       >>> del config['data']
       >>> config.dump()
       x_value = 10.1
       y_value = 20.2
       z_value = 30.3
       [velocity]
           filename = 'vel.dat'
           type = 'RAW'
       >>>
    """

    def __init__(self, init=None, *, dictionary=None, defaults=True, schema=None, validate=True):
        super().__init__(dictionary=dictionary, init=init, defaults=defaults, schema=schema, validate=validate)
