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

def touch(dirname, filename):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    filepath = os.path.join(dirname, filename)
    with open(filepath, "w") as f:
        pass
    return filepath

def test_standard_filepath(config_class, protocol):
    filepath = standard_filepath(config=config_class, rootname="root", protocol=protocol)
    filetypes = list(guess(filepath))
    assert len(filetypes) == 1
    filetype = filetypes[0]
    assert filetype.filepath == filepath
    assert filetype.protocol == protocol
    assert filetype.config_class == config_class
    filepath2 = standard_filepath(config=config_class.__name__, rootname="root", protocol=protocol)
    assert filepath2 == filepath
    filepath3 = standard_filepath(config=config_class(), rootname="root", protocol=protocol)
    assert filepath3 == filepath

def test_guess_mult():
    filepath = "/a/b{protocol}/{config_class}/xx.{protocol}-{config_class}"
    filetypes = list(guess(filepath))
    filetypes_d = {filetype.filepath: filetype for filetype in filetypes}
    protocols = get_protocols()
    config_classes = get_config_classes()
    assert len(filetypes) == len(protocols) * len(config_classes)
    for config_class in config_classes:
        for protocol in protocols:
            fp = filepath.format(protocol=protocol, config_class=config_class.__name__.lower())
            assert fp in filetypes_d
            #assert config_class == filetypes_d[fp].config_class
            #assert protocol == filetypes_d[fp].protocol
            #assert FileType(filepath=fp, protocol=protocol, config_class=config_class) == filetypes_d[fp]
            assert FileType(filepath=fp, protocol=protocol, config_class=config_class) in filetypes

def test_guess_no_match():
    filename = "abc.xconfig"
    filetypes = list(guess(filename))
    assert len(filetypes) == 0

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

def test_search_paths(tmpdir):
    cdirs = ['config_a', 'config_b']
    sdirs = ['config_b', 'schema_c']
    os.environ['DAIKON_CONFIG_PATH'] = ':'.join(cdirs)
    os.environ['DAIKON_SCHEMA_PATH'] = ':'.join(sdirs)
    try:
        lst = tuple(search_paths())
    finally:
        del os.environ['DAIKON_CONFIG_PATH']
        del os.environ['DAIKON_SCHEMA_PATH']
    assert lst[0] == (os.getcwd(), get_config_classes())
    assert lst[1] == ('config_a', (Config,))
    assert lst[2] == ('config_b', (Config,))
    assert lst[3] == ('config_b', (Schema,))
    assert lst[4] == ('schema_c', (Schema,))

def test_discover_search(tmpdir):
    tdata = os.path.join(tmpdir.strpath, "DISCOVER")
    tadd = os.path.join(tdata, "ADD")
    tconfig = os.path.join(tdata, "CONFIG")
    tschema = os.path.join(tdata, "SCHEMA")
    os.makedirs(tdata)
    os.makedirs(tadd)
    os.makedirs(tconfig)
    os.makedirs(tschema)
    files = []
    files.append(touch(tconfig, "a.daikon"))
    files.append(touch(tconfig, "b.json"))
    touch(tconfig, "c.daikon-schema")
    files.append(touch(tschema, "d.daikon-schema"))
    touch(tschema, "c.configobj")
    files.append(touch(tdata, "d.pickle"))
    files.append(touch(tdata, "d.pickle-schema"))
    files.append(touch(tadd, "a.json-validation"))
    files.append(touch(tadd, "e.json-schema"))
    es_filepath = files[-1]
    ec_filepath = touch(tadd, "e.configobj")
    os.chdir(tdata)
    os.environ['DAIKON_CONFIG_PATH'] = tconfig
    os.environ['DAIKON_SCHEMA_PATH'] = tschema
    try:
        filetypes = list(discover((tadd, (Validation, Schema))))
        ft_e0_l = list(search_rootname(os.path.join("ADD", "e")))
        ft_e1_l = list(search_rootname(os.path.join("ADD", "e"), config_classes=(Schema,)))
        ft_e2_l = list(search_rootname(os.path.join("ADD", "e"), protocols=("daikon", "json")))
        ft_e3_l = list(search_rootname(os.path.join("ADD", "e"), config_classes=(Schema, Validation), protocols=("daikon", "configobj")))
        ft_e4_l = list(search_rootname(os.path.join("ADD", "e"), config_classes=(Schema, Validation), protocols=("daikon", "json")))
        ftfp_e1_l = list(search_filetype(FileType(filepath=os.path.join("ADD", "e"), config_class=Schema, protocol=None)))
        ftfp_ex_l = list(search_filetype(FileType(filepath=os.path.join("ADD", "e"), config_class=Schema, protocol="pickle")))
    finally:
        del os.environ['DAIKON_CONFIG_PATH']
        del os.environ['DAIKON_SCHEMA_PATH']
    files.sort()
    found_files = [ft.filepath for ft in filetypes]
    found_files.sort()
    #for file in files:
    #    if file not in found_files:
    #        print("expected, not found:", file)
    #for file in found_files:
    #    if file not in files:
    #        print("found, not expected:", file)
    assert files == found_files

    filetypes_d = {filetype.filepath: filetype for filetype in filetypes}
    assert ec_filepath not in filetypes_d
    filetypes_d[ec_filepath] = FileType(filepath=ec_filepath, config_class=Config, protocol="configobj")

    assert len(ft_e0_l) == 2
    dd = {filetype.filepath: filetype for filetype in ft_e0_l}
    assert ec_filepath in dd
    assert dd[ec_filepath] == filetypes_d[ec_filepath]
    assert es_filepath in dd
    assert dd[es_filepath] == filetypes_d[es_filepath]

    assert len(ft_e1_l) == 1
    ft_e1 = ft_e1_l[0]
    assert ft_e1 == FileType(filepath=es_filepath, config_class=Schema, protocol="json")

    assert len(ft_e2_l) == 1
    ft_e2 = ft_e2_l[0]
    assert ft_e2 == ft_e1

    assert len(ft_e3_l) == 0

    assert len(ft_e4_l) == 1
    ft_e4 = ft_e4_l[0]
    assert ft_e4 == ft_e1

    assert len(ftfp_e1_l) == 1
    ftfp_e1 = ftfp_e1_l[0]
    assert ftfp_e1 == ft_e1

    assert len(ftfp_ex_l) == 0
