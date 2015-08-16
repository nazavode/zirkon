# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from common.fixtures import defaultsvalue, \
                            dictionary, \
                            simple_config_content, \
                            string_io, \
                            tmp_raw_file

from daikon.config import Config
from daikon.toolbox.serializer.pickle_serializer import PickleSerializer

@pytest.fixture
def serializer():
    return PickleSerializer()

def test_PickleSerializer_to_from_string(simple_config_content, serializer):
    serialization = serializer.to_string(simple_config_content)
    obj = serializer.from_string(serialization=serialization)
    assert obj == simple_config_content
