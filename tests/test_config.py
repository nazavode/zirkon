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
from daikon.toolbox.deferred import Deferred
from daikon.config import Config
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

def test_Config_to_file_JSON(simple_config, tmp_text_file):
    simple_config.to_file(filename=tmp_text_file.name, protocol="JSON")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_CONFIG_JSON_SERIALIZATION

def test_Config_from_file_JSON(simple_config, tmp_text_file):
    tmp_text_file.write(SIMPLE_CONFIG_JSON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    config = Config.from_file(filename=tmp_text_file.name, protocol="JSON")
    assert config == simple_config

def test_Config_to_file_ConfigObj(simple_config, tmp_text_file):
    simple_config.to_file(filename=tmp_text_file.name, protocol="ConfigObj")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION

def test_Config_from_file_ConfigObj(simple_config, tmp_text_file):
    tmp_text_file.write(SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    config = Config.from_file(filename=tmp_text_file.name, protocol="ConfigObj")
    assert config == simple_config

def test_Config_to_file_Daikon(simple_config, tmp_text_file):
    simple_config.to_file(filename=tmp_text_file.name, protocol="Daikon")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_CONFIG_DAIKON_SERIALIZATION

def test_Config_from_file_Daikon(simple_config, tmp_text_file):
    tmp_text_file.write(SIMPLE_CONFIG_DAIKON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    config = Config.from_file(filename=tmp_text_file.name, protocol="Daikon")
    assert config == simple_config

def test_Config_get_serializer_JSON():
    assert isinstance(Config.get_serializer("JSON"), JSONSerializer)

def test_Config_get_serializer_ConfigObj():
    assert isinstance(Config.get_serializer("ConfigObj"), ConfigObjSerializer)

def test_Config_get_serializer_Pickle():
    assert isinstance(Config.get_serializer("Pickle"), PickleSerializer)

def test_Config_deferred():
    config = Config()
    config['a'] = 10
    config['b'] = 20
    config['c'] = Deferred("SECTION['a'] * SECTION['b']")
    config['sub'] = {}
    config['sub']['x'] = 7
    config['options'] = {}
    config['options']['d'] = 100
    config['options']['e'] = Deferred("ROOT['a'] + ROOT['sub']['x'] + SECTION['d']")

    assert isinstance(config['c'], int)
    assert config['c'] == 200
    assert isinstance(config['options']['e'], int)
    assert config['options']['e'] == 117

def test_Config_deferred_error():
    config = Config()
    config['a'] = 10
    with pytest.raises(KeyError) as exc_info:
        config['c'] = Deferred("SECTION['a'] * SECTION['b']")
    print(exc_info)
    print(exc_info.value)
    assert str(exc_info.value) == "'b'"
    config['b'] = 20
