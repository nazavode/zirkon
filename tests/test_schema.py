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
    defaultsvalue, \
    string_io, \
    tmp_text_file, \
    simple_section_content, \
    simple_schema_content, simple_schema, \
    SIMPLE_SCHEMA_DUMP, \
    SIMPLE_SCHEMA_JSON_SERIALIZATION, \
    SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION, \
    SIMPLE_SCHEMA_ZIRKON_SERIALIZATION

from zirkon.config import Config, ROOT, SECTION
from zirkon.schema import Schema
from zirkon.validator import Int, IntChoice
from zirkon.validator.error import InvalidChoiceError, \
    MinValueError, MaxValueError

from zirkon.toolbox.serializer import JSONSerializer, \
    ConfigObjSerializer, ZirkonSerializer, PickleSerializer

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

def test_Schema_to_file_json(simple_schema, tmp_text_file):
    simple_schema.to_file(filename=tmp_text_file.name, protocol="json")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_SCHEMA_JSON_SERIALIZATION

def test_Schema_from_file_json(simple_schema, tmp_text_file):
    tmp_text_file.write(SIMPLE_SCHEMA_JSON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    schema = Schema.from_file(filename=tmp_text_file.name, protocol="json")
    assert schema == simple_schema

def test_Schema_to_file_configobj(simple_schema, tmp_text_file):
    simple_schema.to_file(filename=tmp_text_file.name, protocol="configobj")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION

def test_Schema_from_file_configobj(simple_schema, tmp_text_file):
    tmp_text_file.write(SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    schema = Schema.from_file(filename=tmp_text_file.name, protocol="configobj")
    assert schema == simple_schema

def test_Schema_to_file_zirkon(simple_schema, tmp_text_file):
    simple_schema.to_file(filename=tmp_text_file.name, protocol="zirkon")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_SCHEMA_ZIRKON_SERIALIZATION

def test_Schema_from_file_zirkon(simple_schema, tmp_text_file):
    tmp_text_file.write(SIMPLE_SCHEMA_ZIRKON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    schema = Schema.from_file(filename=tmp_text_file.name, protocol="zirkon")
    assert schema == simple_schema

def test_Schema_get_serializer_json():
    assert isinstance(Schema.get_serializer("json"), JSONSerializer)

def test_Schema_get_serializer_configobj():
    assert isinstance(Schema.get_serializer("configobj"), ConfigObjSerializer)

def test_Schema_get_serializer_pickle():
    assert isinstance(Schema.get_serializer("pickle"), PickleSerializer)

def test_Schema_get_serializer_zirkon():
    assert isinstance(Schema.get_serializer("zirkon"), ZirkonSerializer)

@pytest.fixture
def macro_schema():
    schema = Schema()
    schema['a'] = Int()
    schema['b'] = Int()
    schema['c'] = IntChoice(choices=(SECTION['a'], SECTION['b']))
    schema['sub'] = {}
    schema['sub']['d'] = Int(min=ROOT['a'], max=ROOT['b'])
    schema['sub']['e'] = Int(default=ROOT['a'] + ROOT['b'] + SECTION['d'])
    return schema

@pytest.fixture
def macro_config(defaultsvalue):
    config = Config(defaults=defaultsvalue)
    config['a'] = 10
    config['b'] = 20
    config['c'] = 10
    config['sub'] = {}
    config['sub']['d'] = 18
    config['sub']['e'] = -100
    return config

def test_Schema_macro_pass(macro_schema, macro_config):
    macro_schema.validate(macro_config)
    assert macro_config['c'] == 10
    assert macro_config['sub']['e'] == -100

def test_Schema_macro_default(macro_schema, macro_config):
    del macro_config['sub']['e']
    macro_schema.validate(macro_config)
    assert macro_config['c'] == 10
    assert macro_config['sub']['e'] == 48
    macro_config['b'] = -10
    del macro_config['sub']['e']
    print("==== start")
    macro_schema.validate(macro_config)
    print("==== stop")
    assert macro_config['sub']['e'] == 18
    #if macro_config.defaults() is None:
    #    assert macro_config['sub']['e'] == 18
    #else:
    #    assert macro_config['sub']['e'] == 48

def test_Schema_macro_err_option(macro_schema, macro_config):
    macro_config['c'] = 15
    with pytest.raises(InvalidChoiceError) as exc_info:
        macro_schema.validate(macro_config, raise_on_error=True)
    assert str(exc_info.value) == "c=15: 15 is not a valid choice; valid choices are: (10, 20)"

def test_Schema_macro_err_min(macro_schema, macro_config):
    macro_config['a'] = 19
    macro_config['c'] = macro_config['b']
    with pytest.raises(MinValueError) as exc_info:
        macro_schema.validate(macro_config, raise_on_error=True)
    assert str(exc_info.value) == "sub.d=18: value is lower than min 19"

def test_Schema_macro_err_max(macro_schema, macro_config):
    macro_config['b'] = 13
    macro_config['c'] = macro_config['a']
    with pytest.raises(MaxValueError) as exc_info:
        macro_schema.validate(macro_config, raise_on_error=True)
    assert str(exc_info.value) == "sub.d=18: value is greater than max 13"
