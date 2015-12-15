# -*- coding: utf-8 -*-

import collections
import inspect
import os

import pytest

from common.fixtures import simple_config_content, \
                            dictionary, \
                            defaultsvalue, \
                            string_io, \
                            tmp_text_file, \
                            SIMPLE_CONFIG_ZIRKON_SERIALIZATION

from zirkon.config import Config
from zirkon.toolbox.serializer.zirkon_serializer import ZirkonSerializer

@pytest.fixture
def serializer():
    return ZirkonSerializer()

def test_ZirkonSerializer_to_string(simple_config_content, serializer):
    serialization = serializer.to_string(simple_config_content)
    assert serialization == SIMPLE_CONFIG_ZIRKON_SERIALIZATION

def test_ZirkonSerializer_from_string(simple_config_content, serializer):
    obj = serializer.from_string(serialization=SIMPLE_CONFIG_ZIRKON_SERIALIZATION)
    assert obj == simple_config_content

def test_ZirkonSerializer_to_stream(simple_config_content, serializer, string_io):
    serializer.to_stream(obj=simple_config_content, stream=string_io)
    assert string_io.getvalue() == SIMPLE_CONFIG_ZIRKON_SERIALIZATION

def test_ZirkonSerializer_from_stream(simple_config_content, serializer, string_io):
    string_io.write(SIMPLE_CONFIG_ZIRKON_SERIALIZATION)
    string_io.seek(0)
    obj = serializer.from_stream(stream=string_io)
    assert obj == simple_config_content

def test_ZirkonSerializer_to_file(simple_config_content, serializer, tmp_text_file):
    serializer.to_file(obj=simple_config_content, filename=tmp_text_file.name)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_CONFIG_ZIRKON_SERIALIZATION

def test_ZirkonSerializer_from_file(simple_config_content, serializer, tmp_text_file):
    tmp_text_file.write(SIMPLE_CONFIG_ZIRKON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    obj = serializer.from_file(filename=tmp_text_file.name)
    assert obj == simple_config_content

strings = collections.OrderedDict()
strings['c0'] = """\
[a]
[b]
    x = 10
[c]
    [d]
    [e]
        y = 10
x = 9
[f]
xx = 9
[g]
    [h]
        [i]
    yy = 9
[j]
[k]
[l]
    [m]
        [n]
            [o]
    zz = 1.2
"""

@pytest.fixture(params=list(strings.values()), ids=list(strings.keys()))
def string(request):
    return request.param

def test_ZirkonSerializer(string, serializer):
    obj = serializer.from_string(string)
    string2 = serializer.to_string(obj=obj)
    assert string == string2
