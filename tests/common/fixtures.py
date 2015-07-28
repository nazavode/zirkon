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
    'simple_container',
    'simple_content',
    'simple_section',
    'simple_config',
    'tmp_text_file',
    'tmp_raw_file',
    'SIMPLE_SECTION_DUMP',
    'SIMPLE_SECTION_REPR',
    'SIMPLE_SECTION_STR',
    'SIMPLE_CONFIG_JSON_SERIALIZATION',
    'SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION',
]

import collections
import io
import tempfile

import pytest

from config.section import Section
from config.config import Config

@pytest.fixture
def string_io():
    return io.StringIO()

@pytest.fixture
def simple_container():
    return collections.OrderedDict()

@pytest.fixture
def simple_content():
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
def simple_section(simple_container, simple_content):
    section = Section(container=simple_container, init=simple_content)
    return section

@pytest.fixture
def simple_config(simple_container, simple_content):
    config = Config(container=simple_container, init=simple_content)
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

