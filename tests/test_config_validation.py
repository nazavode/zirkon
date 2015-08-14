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

from common.fixtures import string_io

from daikon.toolbox.dictutils import compare_dicts
from daikon.config import Config, ConfigValidationError
from daikon.schema import Schema
from daikon.validator import Str, StrChoice, Float, Int, FloatList

@pytest.fixture
def schema():
    schema = Schema()
    schema['filename'] = Str()
    schema['run_mode'] = StrChoice(choices=("alpha", "beta", "gamma"))
    schema['values'] = {}
    schema['values']['x'] = Float(min=10.0, max=20.0)
    schema['values']['y'] = Float(min=10.0, max=20.0)
    schema['values']['z'] = Float(min=10.0, max=20.0)
    schema['operation'] = StrChoice(choices=("+", "-"))
    schema['parameters'] = {}
    schema['parameters']['max_iterations'] = Int(default=100)
    schema['parameters']['frequencies'] = FloatList(min_len=2)
    return schema

@pytest.fixture
def config_content():
    config_content = collections.OrderedDict()
    config_content['filename'] = "x.dat"
    config_content['run_mode'] = "beta"
    config_content['values'] = collections.OrderedDict()
    config_content['values']['x'] = 11.2
    config_content['values']['y'] = 12.2
    config_content['values']['z'] = 13.2
    config_content['operation'] = "+"
    config_content['parameters'] = collections.OrderedDict()
    config_content['parameters']['max_iterations'] = 80
    config_content['parameters']['frequencies'] = [5.0, 10.0, 15.0]
    return config_content

@pytest.fixture
def config(config_content, schema):
    return Config(config_content, schema=schema)

CONFIG_DUMP = """\
filename = 'x.dat'
run_mode = 'beta'
[values]
    x = 11.2
    y = 12.2
    z = 13.2
operation = '+'
[parameters]
    max_iterations = 80
    frequencies = [5.0, 10.0, 15.0]
"""

def test_Config(string_io, config, config_content):
    config.dump(stream=string_io)
    assert string_io.getvalue() == CONFIG_DUMP

def test_Config_self_validate(string_io, config):
    config.self_validate(raise_on_error=True)

def test_Config_self_validate_default(string_io, config):
    assert 'max_iterations' in config['parameters']
    assert config['parameters']['max_iterations'] == 80
    del config['parameters']['max_iterations']
    assert not 'max_iterations' in config['parameters']
    config.self_validate(raise_on_error=True)
    assert 'max_iterations' in config['parameters']
    assert config['parameters']['max_iterations'] == 100

def test_Config_self_validate_error(string_io, config):
    print(config.schema)
    del config['parameters']['frequencies'][1:]
    print(config.schema)
    assert len(config['parameters']['frequencies'])
    with pytest.raises(ConfigValidationError) as exc_info:
        x = config.self_validate(raise_on_error=True)
        x.dump()
    assert str(exc_info.value) == "validation error: Validation(parameters=ValidationSection(frequencies=MinLengthError('parameters.frequencies=[5.0]: value has length 1 than is lower than min_len 2',)))"
    exc_info.value.validation.dump(string_io)
    assert string_io.getvalue() == """\
[parameters]
    frequencies = MinLengthError('parameters.frequencies=[5.0]: value has length 1 than is lower than min_len 2')
"""

def test_Config_self_validate_error_dump(string_io, config):
    del config['parameters']['frequencies'][1:]
    assert len(config['parameters']['frequencies'])
    with pytest.raises(ConfigValidationError) as exc_info:
        config.dump()
    assert str(exc_info.value) == "validation error: Validation(parameters=ValidationSection(frequencies=MinLengthError('parameters.frequencies=[5.0]: value has length 1 than is lower than min_len 2',)))"
    exc_info.value.validation.dump(string_io)
    assert string_io.getvalue() == """\
[parameters]
    frequencies = MinLengthError('parameters.frequencies=[5.0]: value has length 1 than is lower than min_len 2')
"""
