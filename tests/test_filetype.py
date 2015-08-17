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
import os

import pytest

from common.fixtures import protocol

from daikon.config_base import ConfigBase
from daikon.config import Config
from daikon.schema import Schema
from daikon.validation import Validation

from daikon.filetype import guess, standard_filepath, classify, \
    get_config_classes, get_protocols, FileType, \
    discover, search_paths, search_rootname, search_filetype

@pytest.fixture(params=[Config, Schema, Validation])
def config_class(request):
    return request.param

@pytest.fixture
def config_class_name(config_class):
    return config_class.__name__

def test_standard_filepath(config_class, protocol):
    filepath = standard_filepath(config=config_class, rootname="root", protocol=protocol)
    filetype = guess(filepath)
    assert filetype.filepath == filepath
    assert filetype.protocol == protocol
    assert filetype.config_class == config_class
    filepath2 = standard_filepath(config=config_class.__name__, rootname="root", protocol=protocol)
    assert filepath2 == filepath
    filepath3 = standard_filepath(config=config_class(), rootname="root", protocol=protocol)
    assert filepath3 == filepath

def test_guess_err():
    filename = "abc.xconfig"
    filetype = guess(filename)
    assert filetype.filepath == filename
    assert filetype.protocol is None
    assert filetype.config_class is None

def test_classify(tmpdir):
    config_classes = get_config_classes()
    protocols = get_protocols()
    ref_filetypes = {}
    for rootname in 'x', 'xy':
        for config_class in config_classes:
            for protocol in protocols:
                filename = standard_filepath(rootname=rootname, config=config_class, protocol=protocol)
                filepath = os.path.join(tmpdir.strpath, filename)
                with open(filepath, "w") as f_out:
                    pass
                ref_filetype = FileType(filepath=filepath, config_class=config_class, protocol=protocol)
                ref_filetypes[filepath] = ref_filetype
    
    for filetype in classify(tmpdir.strpath):
        assert filetype.filepath in ref_filetypes
        ref_filetype = ref_filetypes.pop(filetype.filepath)
        assert filetype == ref_filetype
        os.remove(filetype.filepath)
    assert len(ref_filetypes) == 0

def test_classify_config_classes_protocols(tmpdir):
    for filetype in classify(tmpdir.strpath, config_classes=("Config", "Schema"), protocols=("daikon", "json")):
        pass

def test_classify_class(tmpdir):
    for filetype in classify(tmpdir.strpath, config_classes=(Config, Schema), protocols=("daikon", "json")):
        pass

def test_classify_class_error(tmpdir):
    with pytest.raises(TypeError) as exc_info:
        for x in classify(tmpdir.strpath, config_classes=(Config, Schema, ConfigBase)):
            pass
    assert str(exc_info.value) == "unsupported config_class <class 'daikon.config_base.ConfigBase'>"

def test_classify_class_name_error(tmpdir):
    with pytest.raises(ValueError) as exc_info:
        for x in classify(tmpdir.strpath, config_classes=(Config, "Skema")):
            pass
    assert str(exc_info.value) == "unsupported config_class name 'Skema'"

def test_classify_class_type_error(tmpdir):
    with pytest.raises(ValueError) as exc_info:
        for x in classify(tmpdir.strpath, config_classes=(Config, 0.3)):
            pass
    assert str(exc_info.value) == "invalid object 0.3 of type float: not a config[_class]"

def test_classify_protocol_error(tmpdir):
    with pytest.raises(ValueError) as exc_info:
        for x in classify(tmpdir.strpath, protocols=("json", "yaml")):
            pass
    assert str(exc_info.value) == "unsupported protocol 'yaml'"

def test_classify_search_paths(tmpdir):
    cdirs = ['config_a', 'config_b']
    sdirs = ['config_b', 'schema_c']
    os.environ['DAIKON_CONFIG_PATH'] = ':'.join(cdirs)
    os.environ['DAIKON_SCHEMA_PATH'] = ':'.join(sdirs)
    try:
        lst = tuple(search_paths())
        assert lst[0] == (os.getcwd(), get_config_classes())
        assert lst[1] == ('config_a', (Config,))
        assert lst[2] == ('config_b', (Config,))
        assert lst[3] == ('config_b', (Schema,))
        assert lst[4] == ('schema_c', (Schema,))
    finally:
        del os.environ['DAIKON_CONFIG_PATH']
        del os.environ['DAIKON_SCHEMA_PATH']
