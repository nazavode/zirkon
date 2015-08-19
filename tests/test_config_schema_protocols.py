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

import collections
import io

import pytest

from common.fixtures import protocol, \
    simple_config_content, simple_schema_content, \
    simple_section_content, simple_validation, tmp_text_file

from zirkon.config import Config, SECTION, ROOT
from zirkon.schema import Schema
from zirkon.validation import Validation
from zirkon.validator import Int
from zirkon.validator.error import MinValueError
from zirkon.toolbox.dictutils import compare_dicts, transform
from zirkon.toolbox.serializer import Serializer

Parameters = collections.namedtuple('Parameters', ('config_class', 'config_content'))

validation = simple_validation(
    simple_schema_content=simple_schema_content(),
    simple_section_content=simple_section_content(),
)

_config_parameters = [
    Parameters(config_class=Config, config_content=simple_config_content()),
    Parameters(config_class=Schema, config_content=simple_schema_content()),
    Parameters(config_class=Validation, config_content=validation),
]
@pytest.fixture(params=_config_parameters, ids=[c.config_class.__name__ for c in _config_parameters])
def parameters(request):
    return request.param

def test_read_write(protocol, parameters, tmp_text_file):
    config_class = parameters.config_class
    config_content = parameters.config_content
    cs = config_class(config_content)

    print(":::", config_class)
    cs.dump()

    cs.write(tmp_text_file.name, protocol)
    cs2 = config_class()
    cs2.read(tmp_text_file.name, protocol)

    print("::: reloaded:")
    cs2.dump()

    if config_class == Validation:
        tcs = transform(cs, value_transform=str, dict_class=dict)
        tcs2 = transform(cs2, value_transform=str, dict_class=dict)
        print("===", type(tcs), type(tcs2))
        assert tcs == tcs2
    else:
        assert compare_dicts(cs, cs2)

@pytest.fixture
def schema_de():
    schema = Schema()
    schema['alpha'] = Int(default=10)
    schema['beta'] = Int(default=ROOT['alpha'] - 3)
    schema['sub'] = {}
    schema['sub']['x'] = Int(min=ROOT['beta'])
    schema['sub']['y'] = Int(default=ROOT['alpha'] + SECTION['x'])
    schema['sub']['z'] = Int(default=0)
    return schema

SCHEMA_DE_STRING = {}
SCHEMA_DE_STRING['zirkon'] = """\
alpha = Int(default=10)
beta = Int(default=ROOT['alpha'] - 3)
[sub]
    x = Int(min=ROOT['beta'])
    y = Int(default=ROOT['alpha'] + SECTION['x'])
    z = Int(default=0)
"""
SCHEMA_DE_STRING['configobj'] = SCHEMA_DE_STRING['zirkon']

def test_read_write_schema_de(protocol, schema_de):
    schema_de_string = schema_de.to_string(protocol=protocol)
    ref_schema_de_string = SCHEMA_DE_STRING.get(protocol, None)
    if ref_schema_de_string:
        assert schema_de_string == ref_schema_de_string
    schema_de_reloaded = Schema.from_string(schema_de_string, protocol=protocol)
    assert schema_de == schema_de_reloaded
    schema_de_reloaded_string = schema_de_reloaded.to_string(protocol=protocol)
    if ref_schema_de_string:
        assert schema_de_reloaded_string == schema_de_string
    else:
        assert schema_de_reloaded.to_string(protocol='zirkon') == schema_de.to_string(protocol='zirkon')

CONFIG_DE_STRING = {}
CONFIG_DE_STRING['zirkon'] = """\
[sub]
    x = 100
    z = SECTION['x'] + 5
"""
CONFIG_DE_STRING['configobj'] = CONFIG_DE_STRING['zirkon']

@pytest.fixture
def config_de():
    config = Config()
    config['sub'] = {}
    config['sub']['x'] = 100
    config['sub']['z'] = SECTION['x'] + 5
    return config

@pytest.fixture
def config_protocol(protocol, config_de):
    ref_config_de_string = CONFIG_DE_STRING.get(protocol, None)
    if ref_config_de_string:
        config = Config.from_string(ref_config_de_string, protocol=protocol)
    else:
        config = config_de
    return config, protocol

def test_read_write_config_de(config_protocol):
    config, protocol = config_protocol
    assert config['sub']['z'] == 105
    config_string = config.to_string(protocol=protocol)
    config_reloaded = Config.from_string(config_string, protocol=protocol)
    assert config_reloaded == config

def test_validate_config_de_ok(config_protocol, schema_de):
    config, protocol = config_protocol
    validation = schema_de.validate(config)
    assert not validation
    assert config['alpha'] == 10
    assert config['beta'] == 7
    assert config['sub']['x'] == 100
    assert config['sub']['y'] == 110
    assert config['sub']['z'] == 105

def test_validate_config_de_ko_min(config_protocol, schema_de):
    config, protocol = config_protocol
    config['sub']['x'] = 1
    validation = schema_de.validate(config)
    assert len(validation) == 1
    assert 'sub' in validation
    assert len(validation['sub']) == 1
    assert 'x' in validation['sub']
    assert isinstance(validation['sub']['x'], MinValueError)
    assert str(validation['sub']['x']) == "sub.x=1: value is lower than min 7"
    assert config['alpha'] == 10
    assert config['beta'] == 7
    assert config['sub']['x'] == 1
    assert config['sub']['y'] == 11
    assert config['sub']['z'] == 6
