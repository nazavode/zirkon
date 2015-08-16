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
import contextlib
import io
import os

import pytest

from common.fixtures import string_io

from daikon.config_base import ConfigBase
from daikon.config import Config
from daikon.schema import Schema
from daikon.validation import Validation

from daikon.filetype import guess, standard_filepath, classify, \
    get_config_classes, get_protocols, FileType

from daikon.tool import main

class Files(collections.OrderedDict):
    def __init__(self, temporary_dir):
        self.temporary_dir = temporary_dir
        super().__init__()

    def add(self, filename):
        tmp_filename = self.get(filename)
        self[filename] = tmp_filename
        return tmp_filename

    def get(self, filename):
        return os.path.join(self.temporary_dir, filename)

    @contextlib.contextmanager
    def tmp(self, *filenames):
        tmp_filenames = []
        for fn in filenames:
            tfn = self.add(fn)
            tmp_filenames.append(tfn)
        yield tuple(tmp_filenames)
        for fn, tfn in zip(filenames, tmp_filenames):
            if os.path.exists(tfn):
                print("remove file {}".format(tfn))
                os.remove(tfn)
            else:
                print("{} *not* found".format(tfn))
            print("remove key {}".format(fn))
            del self[fn]
        
@pytest.fixture
def files(tmpdir):
    fls = Files(temporary_dir=tmpdir.strpath)

    fls.add('x.daikon')
    with open(fls["x.daikon"], "w") as f_out:
        f_out.write("""\
a = 100
b = 1.4
[sub]
    name = "xyz"
    x = 10
    [fun0]
        enable = True
        value = 0.4
""")
    config = Config()
    config.read(fls["x.daikon"], protocol="daikon")
    fls.add("x.json")
    config.write(fls["x.json"], protocol="json")
    fls.add("xwrong.daikon")
    config.write(fls["xwrong.daikon"], protocol="json")

    fls.add('x.daikon-schema')
    with open(fls["x.daikon-schema"], "w") as f_out:
        f_out.write("""\
a = Int()
b = Float()
c = Float(default=ROOT['a'] * ROOT['b'])
[sub]
    name = Str(min_len=1)
    x = Float(min=0.0)
    y = Float(min=0.0)
    [fun0]
        enable = Bool()
        value = Float()
""")
    return fls

def run(args):
    log_stream = string_io()
    out_stream = string_io()
    print(args)
    main(
        log_stream=log_stream,
        out_stream=out_stream,
        args=args,
    )
    return log_stream, out_stream

FIN = collections.namedtuple('FN', ('name', 'protocol', 'force_protocol', 'schema'))
FOUT = collections.namedtuple('FN', ('name', 'protocol', 'force_protocol'))

_in_data = [
    FIN(name="x.daikon", protocol="daikon", force_protocol=None, schema="x.daikon-schema"),
    FIN(name="x.json", protocol="json", force_protocol=None, schema="x.daikon-schema"),
    FIN(name="x.json", protocol="json", force_protocol="json", schema=None),
    FIN(name="xwrong.daikon", protocol="json", force_protocol="json", schema="x.daikon-schema"),
]

_out_data = [
    FOUT(name="out_x.json", protocol="json", force_protocol=None),
    FOUT(name="out_x.json", protocol="configobj", force_protocol="configobj"),
    FOUT(name="out_x.no_protocol", protocol=None, force_protocol=None),
]

@pytest.fixture(params=_in_data)
def in_name_protocol_schema(request):
    return request.param

@pytest.fixture(params=_out_data)
def out_name_protocol(request):
    return request.param

def test_main_read_write(files, in_name_protocol_schema, out_name_protocol):
    in_name, in_protocol, in_force_protocol, in_schema = in_name_protocol_schema
    out_name, out_protocol, out_force_protocol = out_name_protocol
    if out_protocol is None:
        out_protocol = in_protocol
    with files.tmp(out_name):
        in_file_arg = files[in_name]
        if in_force_protocol:
            in_file_arg += ":" + in_force_protocol
        out_file_arg = files[out_name]
        if out_force_protocol:
            out_file_arg += ":" + out_force_protocol
        print(":::>", files[out_name], out_file_arg)
        assert not os.path.exists(files[out_name])
        run(["-c", in_file_arg, "-co", out_file_arg])
        assert os.path.exists(files[out_name])
        print("read in {}:{}".format(files[in_name], in_protocol))
        config1 = Config.from_file(files[in_name], protocol=in_protocol)
        print("read out {}:{}".format(files[out_name], out_protocol))
        config2 = Config.from_file(files[out_name], protocol=out_protocol)
        assert config1 == config2
        out_x_json_path = files[out_name]
    assert not out_name in files
    assert not os.path.exists(out_x_json_path)
    
def xtest_main_read_write_no_protocol(files):
    files.add("out_x.no_protocol")
    print(files["out_x.json"])
    assert not os.path.exists(files["out_x.json"])
    run(["-c", files["x.daikon"], "-co", files["out_x.json"]])
    assert os.path.exists(files["out_x.json"])
    config1 = Config.from_file(files["x.daikon"], protocol="daikon")
    config2 = Config.from_file(files["out_x.json"], protocol="json")
    assert config1 == config2
    
#def xtest_main1(example_files):
#    print('1')
#    assert not os.path.exists("out_x.json")
#    run(["-c", "x.daikon", "-co", "out_x.json"])
#    assert os.path.exists("out_x.json")
#    config1 = Config.from_file("x.daikon", protocol="daikon")
#    config2 = Config.from_file("out_x.json", protocol="json")
#    assert config1 == config2
    
