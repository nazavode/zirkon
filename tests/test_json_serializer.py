# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from common.fixtures import defaultsvalue, \
                            dictionary, \
                            simple_config_content, \
                            string_io, \
                            tmp_text_file, \
                            SIMPLE_CONFIG_JSON_SERIALIZATION

from daikon.config import Config
from daikon.toolbox.serializer.json_serializer import JSONSerializer

@pytest.fixture
def serializer():
    return JSONSerializer()

def test_JSONSerializer_to_string(simple_config_content, serializer):
    serialization = serializer.to_string(simple_config_content)
    assert serialization == SIMPLE_CONFIG_JSON_SERIALIZATION

def test_JSONSerializer_from_string(simple_config_content, serializer):
    obj = serializer.from_string(serialization=SIMPLE_CONFIG_JSON_SERIALIZATION)
    assert obj == simple_config_content

def test_JSONSerializer_to_stream(simple_config_content, serializer, string_io):
    serializer.to_stream(obj=simple_config_content, stream=string_io)
    assert string_io.getvalue() == SIMPLE_CONFIG_JSON_SERIALIZATION

def test_JSONSerializer_from_stream(simple_config_content, serializer, string_io):
    string_io.write(SIMPLE_CONFIG_JSON_SERIALIZATION)
    string_io.seek(0)
    obj = serializer.from_stream(stream=string_io)
    assert obj == simple_config_content

def test_JSONSerializer_to_file(simple_config_content, serializer, tmp_text_file):
    serializer.to_file(obj=simple_config_content, filename=tmp_text_file.name)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_CONFIG_JSON_SERIALIZATION

def test_JSONSerializer_from_file(simple_config_content, serializer, tmp_text_file):
    tmp_text_file.write(SIMPLE_CONFIG_JSON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    obj = serializer.from_file(filename=tmp_text_file.name)
    assert obj == simple_config_content

