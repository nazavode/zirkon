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
    'generic_dictionary',
    'dictionary',
    'protocol',
    'simple_config_content',
    'simple_section',
    'defaultsvalue',
    'simple_config',
    'simple_schema',
    'simple_schema_content',
    'simple_section_content',
    'simple_validation',
    'tmp_text_file',
    'tmp_raw_file',
    'SIMPLE_SECTION_DUMP',
    'SIMPLE_SECTION_REPR',
    'SIMPLE_SECTION_STR',
    'SIMPLE_CONFIG_JSON_SERIALIZATION',
    'SIMPLE_CONFIG_ZIRKON_SERIALIZATION',
    'SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION',
    'SIMPLE_SCHEMA_DUMP',
    'SIMPLE_SCHEMA_JSON_SERIALIZATION',
    'SIMPLE_SCHEMA_ZIRKON_SERIALIZATION',
    'SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION',
]

import collections
import io
import tempfile

import pytest

from zirkon.flatmap import FlatMap
from zirkon.section import Section
from zirkon.config import Config
from zirkon.schema import Schema
from zirkon.validator import Int, Str, StrChoice, Float, FloatTuple
from zirkon.toolbox.serializer import Serializer

@pytest.fixture(params=tuple(Serializer.get_class_tags()))
def protocol(request):
    return request.param

@pytest.fixture
def string_io():
    return io.StringIO()

_dictionary_classes = [dict, collections.OrderedDict, type(None), lambda: FlatMap(collections.OrderedDict())]
@pytest.fixture(params=_dictionary_classes, ids=[cc.__name__ for cc in _dictionary_classes])
def generic_dictionary(request):
    dictionary_class = request.param
    return dictionary_class()

@pytest.fixture
def dictionary():
    return collections.OrderedDict()

# late evaluation through lambda to force a new {} is generated 
@pytest.fixture(params=[lambda: True, lambda: False, lambda: {}])
def defaultsvalue(request):
    return request.param()

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
def simple_section(dictionary, simple_config_content):
    section = Section(dictionary=dictionary, init=simple_config_content)
    return section

@pytest.fixture
def simple_config(dictionary, simple_config_content, defaultsvalue):
    config = Config(dictionary=dictionary, init=simple_config_content, defaults=defaultsvalue)
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

SIMPLE_SECTION_REPR_FLAT = "Section(dictionary=OrderedDict([('x_value', 10.1), ('y_value', 20.2), ('options.i_alpha', 100), ('options.f_beta', -0.123), ('options.b_gamma', True), ('options.epsilon.epsilon_x', 10), ('options.epsilon.epsilon_y', 20), ('options.epsilon.epsilon_z', 30), ('options.epsilon.', None), ('options.s_delta', 'delta.dat'), ('options.', None), ('z_value', 30.3), ('miscellanea.a', 1), ('miscellanea.b', 2), ('miscellanea.', None)]), prefix='')"

SIMPLE_SECTION_REPR = "Section(dictionary=OrderedDict([('x_value', 10.1), ('y_value', 20.2), ('options', OrderedDict([('i_alpha', 100), ('f_beta', -0.123), ('b_gamma', True), ('epsilon', OrderedDict([('epsilon_x', 10), ('epsilon_y', 20), ('epsilon_z', 30)])), ('s_delta', 'delta.dat')])), ('z_value', 30.3), ('miscellanea', OrderedDict([('a', 1), ('b', 2)]))]))"

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

SIMPLE_CONFIG_ZIRKON_SERIALIZATION = SIMPLE_SECTION_DUMP

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
                           ('ssx', StrChoice(choices=["alpha", "beta", "gamma"])),    # list, non tuple: JSON does not preserve tuples!
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
        ssx = StrChoice(choices=['alpha', 'beta', 'gamma'])
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
def simple_schema(dictionary, simple_schema_content):
    schema = Schema(dictionary=dictionary, init=simple_schema_content)
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
                "__class_name__": "StrChoice",
                "choices": [
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
a = Int(min=1)
[sub]
    sa = Float(max=10)
    sb = Int(default=3)
    sc = Str()
    [[subsub]]
        ssx = StrChoice(choices=['alpha', 'beta', 'gamma'])
        ssy = FloatTuple(item_max=5.5)
"""     

SIMPLE_SCHEMA_ZIRKON_SERIALIZATION = SIMPLE_SCHEMA_DUMP

###
@pytest.fixture
def simple_validation(simple_schema_content, simple_section_content):
    schema = Schema(simple_schema_content)
    simple_section_content['a'] = -10
    simple_section_content['sub']['sa'] = 100.3
    simple_section_content['sub']['sb'] = "abc"
    simple_section_content['sub']['sc'] = True
    simple_section_content['sub']['subsub']['ssx'] = "omega"
    simple_section_content['sub']['subsub']['ssy'] = []
    config = Config(simple_section_content)
    return schema.validate(config)


