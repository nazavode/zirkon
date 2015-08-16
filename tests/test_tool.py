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

from daikon.filetype import guess, standard_filepath, \
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
        if filename:
            return os.path.join(self.temporary_dir, filename)
        else:
            return filename

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

FN = collections.namedtuple('FN', ('name', 'protocol', 'force_protocol'))

_ic_data = [
    FN(name="x.daikon", protocol="daikon", force_protocol=None),
    FN(name="x.json", protocol="json", force_protocol=None),
    FN(name="x.json", protocol="json", force_protocol="json"),
    FN(name="xwrong.daikon", protocol="json", force_protocol="json"),
]

_oc_data = [
    FN(name="out_x.json", protocol="json", force_protocol=None),
    FN(name="out_x.json", protocol="configobj", force_protocol="configobj"),
    FN(name="out_x.no_protocol", protocol=None, force_protocol=None),
    FN(name="", protocol=None, force_protocol=None),
    FN(name="", protocol="configobj", force_protocol="configobj"),
]

@pytest.fixture(params=_ic_data)
def ic_name_protocol(request):
    return request.param

@pytest.fixture(params=_oc_data)
def oc_name_protocol(request):
    return request.param

def test_main_read_write(files, ic_name_protocol, oc_name_protocol):
    ic_name, ic_protocol, ic_force_protocol = ic_name_protocol
    oc_name, oc_protocol, oc_force_protocol = oc_name_protocol
    if oc_protocol is None:
        oc_protocol = ic_protocol
    with files.tmp(oc_name):
        ic_file_arg = files[ic_name]
        if ic_force_protocol:
            ic_file_arg += ":" + ic_force_protocol
        oc_file_arg = files[oc_name]
        if oc_force_protocol:
            oc_file_arg += ":" + oc_force_protocol
        print(":::>", files[oc_name], oc_file_arg)

        if oc_name:
            assert not os.path.exists(files[oc_name])

        args = ["-c", ic_file_arg, "-co", oc_file_arg]
        log_stream, out_stream = run(args)

        if oc_name:
            assert os.path.exists(files[oc_name])

        print("read in {}:{}".format(files[ic_name], ic_protocol))
        i_config = Config.from_file(files[ic_name], protocol=ic_protocol)
        print("read out {}:{}".format(files[oc_name], oc_protocol))
        if oc_name:
            o_config = Config.from_file(files[oc_name], protocol=oc_protocol)
        else:
            o_config = Config.from_string(out_stream.getvalue(), protocol=oc_protocol)
        assert i_config == o_config
        out_x_json_path = files[oc_name]
    assert not oc_name in files
    assert not os.path.exists(out_x_json_path)
    
