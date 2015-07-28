# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from common.fixtures import simple_config, \
                            simple_container, \
                            simple_content, \
                            string_io, \
                            tmp_raw_file

from config.config import Config
from config.serializer.pickle_serializer import PickleSerializer

@pytest.fixture
def serializer():
    return PickleSerializer()

def test_PickleSerializer_to_from_string(simple_config, serializer):
    serialization = serializer.to_string(simple_config)
    config = serializer.from_string(config_class=Config, serialization=serialization)
    assert config == simple_config
