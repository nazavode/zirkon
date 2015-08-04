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

from common.fixtures import container, \
    string_io, \
    tmp_text_file, \
    simple_section_content, \
    simple_schema_content, simple_schema, \
    SIMPLE_SCHEMA_DUMP, \
    SIMPLE_SCHEMA_JSON_SERIALIZATION, \
    SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION

from daikon.config import Config
from daikon.schema import Schema

from daikon.serializer import JSONSerializer, \
                              ConfigObjSerializer, \
                              PickleSerializer

def test_Schema_create_empty(string_io):
    schema = Schema()
    schema.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_Schema_create_container(container, string_io):
    schema = Schema(container=container)
    schema.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_Schema_create_init(container, simple_schema_content, string_io):
    schema = Schema(init=simple_schema_content)
    schema.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SCHEMA_DUMP
    assert len(container) == 0

def test_Schema_create_container_init(container, simple_schema_content, string_io):
    schema = Schema(container=container, init=simple_schema_content)
    schema.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SCHEMA_DUMP
    assert len(container) > 0

def test_Schema_to_file_JSON(simple_schema, tmp_text_file):
    simple_schema.to_file(filename=tmp_text_file.name, protocol="JSON")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_SCHEMA_JSON_SERIALIZATION

def test_Schema_from_file_JSON(simple_schema, tmp_text_file):
    tmp_text_file.write(SIMPLE_SCHEMA_JSON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    schema = Schema.from_file(filename=tmp_text_file.name, protocol="JSON")
    assert schema == simple_schema

def test_Schema_to_file_ConfigObj(simple_schema, tmp_text_file):
    simple_schema.to_file(filename=tmp_text_file.name, protocol="ConfigObj")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION

def test_Schema_from_file_ConfigObj(simple_schema, tmp_text_file):
    tmp_text_file.write(SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    schema = Schema.from_file(filename=tmp_text_file.name, protocol="ConfigObj")
    assert schema == simple_schema

def test_Schema_get_serializer_JSON():
    assert isinstance(Schema.get_serializer("JSON"), JSONSerializer)

def test_Schema_get_serializer_ConfigObj():
    assert isinstance(Schema.get_serializer("ConfigObj"), ConfigObjSerializer)

def test_Schema_get_serializer_Pickle():
    assert isinstance(Schema.get_serializer("Pickle"), PickleSerializer)
