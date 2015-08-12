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
    string_io, \
    tmp_text_file, \
    simple_section_content, \
    simple_schema_content, simple_schema, \
    SIMPLE_SCHEMA_DUMP, \
    SIMPLE_SCHEMA_JSON_SERIALIZATION, \
    SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION, \
    SIMPLE_SCHEMA_DAIKON_SERIALIZATION

from daikon.config import Config
from daikon.schema import Schema
from daikon.validator import Int, IntOption
from daikon.validator.error import OptionValueError, \
    MinValueError, MaxValueError
from daikon.toolbox.deferred import Deferred

from daikon.toolbox.serializer import JSONSerializer, \
    ConfigObjSerializer, DaikonSerializer, PickleSerializer

def test_Schema_create_empty(string_io):
    schema = Schema()
    schema.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_Schema_create_dictionary(dictionary, string_io):
    schema = Schema(dictionary=dictionary)
    schema.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_Schema_create_init(dictionary, simple_schema_content, string_io):
    schema = Schema(init=simple_schema_content)
    schema.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SCHEMA_DUMP
    assert len(dictionary) == 0

def test_Schema_create_dictionary_init(dictionary, simple_schema_content, string_io):
    schema = Schema(dictionary=dictionary, init=simple_schema_content)
    schema.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SCHEMA_DUMP
    assert len(dictionary) > 0

def test_Schema_to_file_JSON(simple_schema, tmp_text_file):
    simple_schema.to_file(filename=tmp_text_file.name, protocol="json")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_SCHEMA_JSON_SERIALIZATION

def test_Schema_from_file_JSON(simple_schema, tmp_text_file):
    tmp_text_file.write(SIMPLE_SCHEMA_JSON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    schema = Schema.from_file(filename=tmp_text_file.name, protocol="json")
    assert schema == simple_schema

def test_Schema_to_file_ConfigObj(simple_schema, tmp_text_file):
    simple_schema.to_file(filename=tmp_text_file.name, protocol="configobj")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION

def test_Schema_from_file_ConfigObj(simple_schema, tmp_text_file):
    tmp_text_file.write(SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    schema = Schema.from_file(filename=tmp_text_file.name, protocol="configobj")
    assert schema == simple_schema

def test_Schema_to_file_Daikon(simple_schema, tmp_text_file):
    simple_schema.to_file(filename=tmp_text_file.name, protocol="daikon")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_SCHEMA_DAIKON_SERIALIZATION

def test_Schema_from_file_Daikon(simple_schema, tmp_text_file):
    tmp_text_file.write(SIMPLE_SCHEMA_DAIKON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    schema = Schema.from_file(filename=tmp_text_file.name, protocol="daikon")
    assert schema == simple_schema

def test_Schema_get_serializer_JSON():
    assert isinstance(Schema.get_serializer("json"), JSONSerializer)

def test_Schema_get_serializer_ConfigObj():
    assert isinstance(Schema.get_serializer("configobj"), ConfigObjSerializer)

def test_Schema_get_serializer_Pickle():
    assert isinstance(Schema.get_serializer("pickle"), PickleSerializer)

@pytest.fixture
def deferred_schema():
    schema = Schema()
    schema['a'] = Int()
    schema['b'] = Int()
    schema['c'] = IntOption(values=(Deferred("SECTION['a']"), Deferred("SECTION['b']")))
    schema['sub'] = {}
    schema['sub']['d'] = Int(min=Deferred("ROOT['a']"), max=Deferred("ROOT['b']"))
    schema['sub']['e'] = Int(default=Deferred("ROOT['a'] + ROOT['b'] + SECTION['d']"))
    return schema

@pytest.fixture
def deferred_config():
    config = Config()
    config['a'] = 10
    config['b'] = 20
    config['c'] = 10
    config['sub'] = {}
    config['sub']['d'] = 18
    config['sub']['e'] = -100
    return config

def test_Schema_deferred_pass(deferred_schema, deferred_config):
    deferred_schema.validate(deferred_config)
    assert deferred_config['c'] == 10
    assert deferred_config['sub']['e'] == -100

def test_Schema_deferred_default(deferred_schema, deferred_config):
    del deferred_config['sub']['e']
    deferred_schema.validate(deferred_config)
    assert deferred_config['c'] == 10
    assert deferred_config['sub']['e'] == 48
    deferred_config['b'] = -10
    del deferred_config['sub']['e']
    deferred_schema.validate(deferred_config)
    assert deferred_config['sub']['e'] == 18

def test_Schema_deferred_err_option(deferred_schema, deferred_config):
    deferred_config['c'] = 15
    with pytest.raises(OptionValueError) as exc_info:
        deferred_schema.validate(deferred_config, raise_on_error=True)
    assert str(exc_info.value) == "c=15: 15 is not a valid option value; valid values are: (10, 20)"

def test_Schema_deferred_err_min(deferred_schema, deferred_config):
    deferred_config['a'] = 19
    deferred_config['c'] = deferred_config['b']
    with pytest.raises(MinValueError) as exc_info:
        deferred_schema.validate(deferred_config, raise_on_error=True)
    assert str(exc_info.value) == "sub.d=18: value 18 is lower than min 19"

def test_Schema_deferred_err_max(deferred_schema, deferred_config):
    deferred_config['b'] = 13
    deferred_config['c'] = deferred_config['a']
    with pytest.raises(MaxValueError) as exc_info:
        deferred_schema.validate(deferred_config, raise_on_error=True)
    assert str(exc_info.value) == "sub.d=18: value 18 is greater than max 13"
