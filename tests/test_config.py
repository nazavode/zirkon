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

from common.utils import compare_dicts
from common.fixtures import simple_container, \
                            simple_content, \
                            simple_config, \
                            string_io, \
                            tmp_text_file, \
                            SIMPLE_SECTION_DUMP, \
                            SIMPLE_CONFIG_JSON_SERIALIZATION, \
                            SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION

from daikon.config import Config
from daikon.serializer import JSONSerializer, \
                              ConfigObjSerializer, \
                              PickleSerializer

def test_Config_create_empty(string_io):
    config = Config()
    config.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_Config_create_container(simple_container, string_io):
    config = Config(container=simple_container)
    config.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_Config_create_init(simple_container, simple_content, string_io):
    config = Config(init=simple_content)
    config.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SECTION_DUMP
    assert len(simple_container) == 0

def test_Config_create_container_init(simple_container, simple_content, string_io):
    config = Config(container=simple_container, init=simple_content)
    config.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SECTION_DUMP
    assert len(simple_container) > 0

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

def test_Config_get_serializer_JSON():
    assert isinstance(Config.get_serializer("JSON"), JSONSerializer)

def test_Config_get_serializer_ConfigObj():
    assert isinstance(Config.get_serializer("ConfigObj"), ConfigObjSerializer)

def test_Config_get_serializer_Pickle():
    assert isinstance(Config.get_serializer("Pickle"), PickleSerializer)

def test_Config_read_write(simple_content, tmp_text_file):
    prefix = 'www.'
    config = Config(simple_content, prefix=prefix)
    for protocol in "JSON", "ConfigObj", "Pickle":
        config.write(tmp_text_file.name, protocol)
        config2 = Config(prefix=prefix)
        config2.read(tmp_text_file.name, protocol)
        assert compare_dicts(config, config2)
