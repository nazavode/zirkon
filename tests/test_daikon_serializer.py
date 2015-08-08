# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from common.fixtures import simple_config_content, \
                            dictionary, \
                            simple_config, \
                            string_io, \
                            tmp_text_file, \
                            SIMPLE_CONFIG_DAIKON_SERIALIZATION

from daikon.config import Config
from daikon.toolbox.serializer.daikon_serializer import DaikonSerializer

@pytest.fixture
def serializer():
    return DaikonSerializer()

def test_DaikonSerializer_to_string(simple_config, serializer):
    serialization = serializer.to_string(simple_config)
    assert serialization == SIMPLE_CONFIG_DAIKON_SERIALIZATION

def test_DaikonSerializer_from_string(simple_config, serializer):
    config = serializer.from_string(config_class=Config, serialization=SIMPLE_CONFIG_DAIKON_SERIALIZATION)
    assert config == simple_config

def test_DaikonSerializer_to_stream(simple_config, serializer, string_io):
    serializer.to_stream(config=simple_config, stream=string_io)
    assert string_io.getvalue() == SIMPLE_CONFIG_DAIKON_SERIALIZATION

def test_DaikonSerializer_from_stream(simple_config, serializer, string_io):
    string_io.write(SIMPLE_CONFIG_DAIKON_SERIALIZATION)
    string_io.seek(0)
    config = serializer.from_stream(config_class=Config, stream=string_io)
    assert config == simple_config

def test_DaikonSerializer_to_file(simple_config, serializer, tmp_text_file):
    serializer.to_file(config=simple_config, filename=tmp_text_file.name)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_CONFIG_DAIKON_SERIALIZATION

def test_DaikonSerializer_from_file(simple_config, serializer, tmp_text_file):
    tmp_text_file.write(SIMPLE_CONFIG_DAIKON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    config = serializer.from_file(config_class=Config, filename=tmp_text_file.name)
    assert config == simple_config
