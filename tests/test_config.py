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

from common.fixtures import dictionary, \
    generic_dictionary, \
    simple_config_content, \
    simple_config, \
    string_io, \
    tmp_text_file, \
    SIMPLE_SECTION_DUMP, \
    SIMPLE_CONFIG_JSON_SERIALIZATION, \
    SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION, \
    SIMPLE_CONFIG_DAIKON_SERIALIZATION

from daikon.toolbox.dictutils import compare_dicts
from daikon.section import Section
from daikon.config_section import ConfigSection
from daikon.config import Config, ROOT, SECTION
from daikon.toolbox.serializer import JSONSerializer, \
    ConfigObjSerializer, PickleSerializer

def test_Config_create_empty(string_io):
    config = Config()
    config.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_Config_create_dictionary(generic_dictionary, string_io):
    config = Config(dictionary=generic_dictionary)
    config.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_Config_create_init(simple_config_content, string_io):
    config = Config(init=simple_config_content)
    config.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SECTION_DUMP

def test_Config_create_dictionary_init(dictionary, simple_config_content, string_io):
    config = Config(dictionary=dictionary, init=simple_config_content)
    config.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SECTION_DUMP
    assert len(dictionary) > 0

def test_Config_create_dictionary_init_overlap(string_io):
    dictionary = collections.OrderedDict()
    dictionary['x'] = 10
    dictionary['y'] = 10
    init = {'a': 20, 'y': 30}
    config = Config(init, dictionary=dictionary)
    assert len(config) == 3
    assert config['x'] == 10
    assert config['y'] == 30
    assert config['a'] == 20

def test_Config_to_file_json(simple_config, tmp_text_file):
    simple_config.to_file(filename=tmp_text_file.name, protocol="json")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_CONFIG_JSON_SERIALIZATION

def test_Config_from_file_json(simple_config, tmp_text_file):
    tmp_text_file.write(SIMPLE_CONFIG_JSON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    config = Config.from_file(filename=tmp_text_file.name, protocol="json")
    assert config == simple_config

def test_Config_to_file_configobj(simple_config, tmp_text_file):
    simple_config.to_file(filename=tmp_text_file.name, protocol="configobj")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION

def test_Config_from_file_configobj(simple_config, tmp_text_file):
    tmp_text_file.write(SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    config = Config.from_file(filename=tmp_text_file.name, protocol="configobj")
    assert config == simple_config

def test_Config_to_file_daikon(simple_config, tmp_text_file):
    simple_config.to_file(filename=tmp_text_file.name, protocol="daikon")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_CONFIG_DAIKON_SERIALIZATION

def test_Config_from_file_daikon(simple_config, tmp_text_file):
    tmp_text_file.write(SIMPLE_CONFIG_DAIKON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    config = Config.from_file(filename=tmp_text_file.name, protocol="daikon")
    assert config == simple_config

def test_Config_get_serializer_json():
    assert isinstance(Config.get_serializer("json"), JSONSerializer)

def test_Config_get_serializer_configobj():
    assert isinstance(Config.get_serializer("configobj"), ConfigObjSerializer)

def test_Config_get_serializer_pickle():
    assert isinstance(Config.get_serializer("pickle"), PickleSerializer)

def test_Config_deferred():
    config = Config()
    config['a'] = 10
    config['b'] = 20
    config['c'] = SECTION['a'] * SECTION['b']
    config['sub'] = {}
    config['sub']['x'] = 7
    config['options'] = {}
    config['options']['d'] = 100
    config['options']['e'] = ROOT['a'] + ROOT['sub']['x'] + SECTION['d']

    assert isinstance(config['c'], int)
    assert config['c'] == 200
    assert isinstance(config['options']['e'], int)
    assert config['options']['e'] == 117

def test_Config_deferred_error():
    config = Config()
    config['a'] = 10
    with pytest.raises(KeyError) as exc_info:
        config['c'] = SECTION['a'] * SECTION['b']
    print(exc_info)
    print(exc_info.value)
    assert str(exc_info.value) == "'b'"
    config['b'] = 20

def test_Config_defaults_option():
    config = Config(defaults=True)
    config.add_defaults(a=10)
    assert 'a' in config
    assert config.has_key('a')
    assert config.has_option('a')
    assert config['a'] == 10
    assert config.get('a') == 10
    assert config.get_option('a') == 10
    assert len(config) == 0
    assert not 'a' in config.dictionary

def test_Config_defaults_section():
    config = Config(defaults=True)
    config.add_defaults(a={'x': 1})
    assert 'a' in config
    assert config.has_key('a')
    assert config.has_section('a')
    assert isinstance(config['a'], Section)
    assert len(config['a']) == 1
    assert config['a'].has_option('x')
    assert config.get('a') == config['a']
    assert config.get_section('a') == config['a']
    config['a'] = {'y': 2}
    assert len(config['a']) == 1
    assert config['a'].has_option('x')
    assert config['a'].has_option('y')
    del config['a']
    assert config.has_section('a')
    assert len(config['a']) == 1
    assert config['a'].has_option('x')
    config['x'] = {}
    assert config.has_section('x')
    del config['x']
    assert not config.has_section('x')

def test_Config_defaults_empty_section():
    config = Config(defaults=True)
    config.add_defaults(a={})
    assert not 'a' in config
    assert not config.has_key('a')
    assert not config.has_section('a')

def test_Config_defaults_copy():
    config = Config(defaults=True)
    config['d'] = 11
    config['e'] = 12
    config.add_defaults(a={}, b=5, c={'x': 7}, d=8)
    config2 = config.copy()
    assert not config2.has_section('a')
    assert config2.has_option('b')
    assert config2['b'] == 5
    assert config2.has_section('c')
    assert len(config2['c']) == 1
    assert config2['c']['x'] == 7
    assert config2.has_option('d')
    assert config2['d'] == 11
    assert config2.has_option('e')
    assert config2['e'] == 12
