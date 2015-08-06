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

__author__ = "Simone Campagna"
__all__ = [
    'string_io',
    'generic_container',
    'container',
    'simple_config_content',
    'simple_section',
    'simple_config',
    'simple_schema',
    'simple_schema_content',
    'simple_section_content',
    'tmp_text_file',
    'tmp_raw_file',
    'SIMPLE_SECTION_DUMP',
    'SIMPLE_SECTION_REPR',
    'SIMPLE_SECTION_STR',
    'SIMPLE_CONFIG_JSON_SERIALIZATION',
    'SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION',
    'SIMPLE_SCHEMA_DUMP',
    'SIMPLE_SCHEMA_JSON_SERIALIZATION',
    'SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION',
]

import collections
import io
import tempfile

import pytest

from daikon.section import Section
from daikon.config import Config
from daikon.schema import Schema
from daikon.validator import Int, Str, StrOption, Float, FloatTuple

@pytest.fixture
def string_io():
    return io.StringIO()

_container_classes = [dict, collections.OrderedDict]
@pytest.fixture(params=_container_classes, ids=[cc.__name__ for cc in _container_classes])
def generic_container(request):
    container_class = request.param
    return container_class()

@pytest.fixture
def container():
    return collections.OrderedDict()

@pytest.fixture
def simple_config_content():
    epsilon = collections.OrderedDict((
        ('epsilon_x', 10),
        ('epsilon_y', 20),
        ('epsilon_z', 30),
    ))
    options = collections.OrderedDict((
        ('i_alpha', 100),
        ('f_beta', -0.123),
        ('b_gamma', True),
        ('epsilon', epsilon),
        ('s_delta', 'delta.dat'),
    ))
    miscellanea = collections.OrderedDict((
        ('a', 1),
        ('b', 2),
    ))
    return collections.OrderedDict((
        ('x_value', 10.1),
        ('y_value', 20.2),
        ('options', options),
        ('z_value', 30.3),
        ('miscellanea', miscellanea),
    ))
    

@pytest.fixture
def simple_section(container, simple_config_content):
    section = Section(container=container, init=simple_config_content)
    return section

@pytest.fixture
def simple_config(container, simple_config_content):
    config = Config(container=container, init=simple_config_content)
    return config

@pytest.fixture
def tmp_text_file():
    return tempfile.NamedTemporaryFile(mode='r+')

@pytest.fixture
def tmp_raw_file():
    return tempfile.NamedTemporaryFile(mode='r+b')

##################

SIMPLE_SECTION_DUMP = """\
x_value = 10.1
y_value = 20.2
[options]
    i_alpha = 100
    f_beta = -0.123
    b_gamma = True
    [epsilon]
        epsilon_x = 10
        epsilon_y = 20
        epsilon_z = 30
    s_delta = 'delta.dat'
z_value = 30.3
[miscellanea]
    a = 1
    b = 2
"""

SIMPLE_SECTION_REPR = "Section(container=OrderedDict([('x_value', 10.1), ('y_value', 20.2), ('options.i_alpha', 100), ('options.f_beta', -0.123), ('options.b_gamma', True), ('options.epsilon.epsilon_x', 10), ('options.epsilon.epsilon_y', 20), ('options.epsilon.epsilon_z', 30), ('options.epsilon.', None), ('options.s_delta', 'delta.dat'), ('options.', None), ('z_value', 30.3), ('miscellanea.a', 1), ('miscellanea.b', 2), ('miscellanea.', None)]), prefix='')"

SIMPLE_SECTION_STR = "Section(x_value=10.1, y_value=20.2, options=Section(i_alpha=100, f_beta=-0.123, b_gamma=True, epsilon=Section(epsilon_x=10, epsilon_y=20, epsilon_z=30), s_delta='delta.dat'), z_value=30.3, miscellanea=Section(a=1, b=2))"

SIMPLE_CONFIG_JSON_SERIALIZATION = """\
{
    "x_value": 10.1,
    "y_value": 20.2,
    "options": {
        "i_alpha": 100,
        "f_beta": -0.123,
        "b_gamma": true,
        "epsilon": {
            "epsilon_x": 10,
            "epsilon_y": 20,
            "epsilon_z": 30
        },
        "s_delta": "delta.dat"
    },
    "z_value": 30.3,
    "miscellanea": {
        "a": 1,
        "b": 2
    }
}
"""

SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION = """\
x_value = 10.1
y_value = 20.2
z_value = 30.3
[options]
    i_alpha = 100
    f_beta = -0.123
    b_gamma = True
    s_delta = 'delta.dat'
    [[epsilon]]
        epsilon_x = 10
        epsilon_y = 20
        epsilon_z = 30
[miscellanea]
    a = 1
    b = 2
"""

##################
@pytest.fixture
def simple_schema_content():
    return collections.OrderedDict((
        ('a', Int(min=1)),
        ('sub', collections.OrderedDict((
            ('sa', Float(max=10)),
            ('sb', Int(default=3)),
            ('sc', Str()),
            ('subsub', collections.OrderedDict((
                           ('ssx', StrOption(values=["alpha", "beta", "gamma"])),    # list, non tuple: JSON does not preserve tuples!
                           ('ssy', FloatTuple(item_max=5.5)),
            ))),
        ))),
    ))

SIMPLE_SCHEMA_DUMP = """\
a = Int(min=1)
[sub]
    sa = Float(max=10)
    sb = Int(default=3)
    sc = Str()
    [subsub]
        ssx = StrOption(values=['alpha', 'beta', 'gamma'])
        ssy = FloatTuple(item_max=5.5)
"""

@pytest.fixture
def simple_section_content():
    return collections.OrderedDict((
        ('a', 10),
        ('sub', collections.OrderedDict((
            ('sa', 0.4),
            ('sb', 10),
            ('sc', "a.dat"),
            ('subsub', collections.OrderedDict((
                ('ssx', "beta"),
                ('ssy', (0.3, 0.4, 0.5, 0.6)),
            ))),
        ))),
    ))

@pytest.fixture
def simple_schema(container, simple_schema_content):
    schema = Schema(container=container, init=simple_schema_content)
    return schema

SIMPLE_SCHEMA_JSON_SERIALIZATION = """\
{
    "a": {
        "__class_name__": "Int",
        "min": 1
    },
    "sub": {
        "sa": {
            "__class_name__": "Float",
            "max": 10
        },
        "sb": {
            "__class_name__": "Int",
            "default": 3
        },
        "sc": {
            "__class_name__": "Str"
        },
        "subsub": {
            "ssx": {
                "__class_name__": "StrOption",
                "values": [
                    "alpha",
                    "beta",
                    "gamma"
                ]
            },
            "ssy": {
                "__class_name__": "FloatTuple",
                "item_max": 5.5
            }
        }
    }
}
"""

SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION = """\
a = <Int>Int(min=1)
[sub]
    sa = <Float>Float(max=10)
    sb = <Int>Int(default=3)
    sc = <Str>Str()
    [[subsub]]
        ssx = <StrOption>StrOption(values=['alpha', 'beta', 'gamma'])
        ssy = <FloatTuple>FloatTuple(item_max=5.5)
"""     

