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

from zirkon.config_base import ConfigBase
from zirkon.config import Config
from zirkon.schema import Schema
from zirkon.validation import Validation

from zirkon.filetype import guess, standard_filepath, \
    get_config_classes, get_protocols, FileType

from zirkon._tool.main import main

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
            if tfn is not None:
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
    os.chdir(tmpdir.strpath)

    fls.add('x.zirkon')
    with open(fls["x.zirkon"], "w") as f_out:
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
    config.read(fls["x.zirkon"], protocol="zirkon")
    fls.add("x.json")
    config.write(fls["x.json"], protocol="json")
    fls.add("xwrong.zirkon")
    config.write(fls["xwrong.zirkon"], protocol="json")

    fls.add('x.zirkon-schema')
    with open(fls["x.zirkon-schema"], "w") as f_out:
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
    schema = Schema.from_file(fls["x.zirkon-schema"], protocol="zirkon")
    fls.add("x.s-json")
    schema.to_file(fls["x.s-json"], protocol="json")

    with open(fls.add("x-def-le.zirkon"), "w") as f_out:
        f_out.write("""\
n = 10
[sub]
    n1 = ROOT['n'] + 1
    [sub]
        n2 = ROOT['n'] * ROOT['sub']['n1']
""")
    with open(fls.add("x-def-ee.zirkon"), "w") as f_out:
        f_out.write("""\
n = 10
[sub]
    n1 = 11
    [sub]
        n2 = 110
""")
    return fls

def run(args, log_stream=None, out_stream=None):
    if log_stream is None:
        log_stream = string_io()
    if out_stream is None:
        out_stream = string_io()
    print(args)
    main(
        log_stream=log_stream,
        out_stream=out_stream,
        argv=args,
    )
    return log_stream, out_stream

@pytest.fixture(params=[0, 1, 2, 3])
def verbose_level(request):
    return request.param

_VLOG  = {}
_VLOG[0] = ""
_VLOG[1] = ""
_VLOG[2] = ""
_VLOG[3] = """\
DEBUG    input_filetype:      None
DEBUG    schema_filetype:     None
DEBUG    output_filetype:     None
DEBUG    validation_filetype: None
"""

def test_main_verbose_level(verbose_level):
    args = ["read"]
    if verbose_level == 0:
        args.append('-q')
    elif verbose_level > 1:
        args.append('-' + ('v' * (verbose_level - 1)))
    args.extend(('-i', "non-existent-path.zirkon"))
    log_stream=string_io()
    out_stream=string_io()
    with pytest.raises(SystemExit) as exc_info:
        run(args, log_stream=log_stream, out_stream=out_stream)
    assert str(exc_info.value) == "1"
    assert log_stream.getvalue() == "ERROR    invalid value non-existent-path.zirkon: input file not found\n"
    assert out_stream.getvalue() == ""


@pytest.fixture(params=[True, False])
def overwrite(request):
    return request.param

def test_main_overwrite_mode(files, overwrite):
    oname = 'xy.zirkon'
    with files.tmp(oname):
        with open(files[oname], "w"):
            pass
        args = ["read", '-i', files['x.zirkon'], '-o', files[oname]]
        if overwrite:
            args.append("-f")

        if overwrite:
            run(args)
        else:
            with pytest.raises(SystemExit):
                log_stream, out_stream = run(args)
                assert out_stream.getvalue() == ""
                assert log_stream.getvalue() == "ERROR    cannot overwrite existing file {!r}\n".format(files[oname])

def test_main_create_template(files, string_io):
    o_name = "x-template.zirkon"
    s_name = "x.zirkon-schema"
    with files.tmp(o_name):
        o_file = files[o_name]
        s_file = files[s_name]

        assert not os.path.exists(files[o_name])

        args = ["create", "-s", s_file, "-o", o_file]
        log_stream, out_stream = run(args)

        config = Config()
        config.read(o_file, protocol="zirkon")
        config.dump(string_io)
        assert string_io.getvalue() == """\
a = '# Int()'
b = '# Float()'
c = ROOT['a'] * ROOT['b']
[sub]
    name = '# Str(min_len=1)'
    x = '# Float(min=0.0)'
    y = '# Float(min=0.0)'
    [fun0]
        enable = '# Bool()'
        value = '# Float()'
"""

@pytest.fixture(params=['x-def-le.zirkon', 'x-def-ee.zirkon'])
def x_def_name(request):
    return request.param

def test_main_macro(files, x_def_name, defaults):
    i_file = files[x_def_name]
    args = ["read", "-i", i_file, "-o", ":zirkon"]
    if defaults is not None:
        args.append("--defaults={!r}".format(defaults))
    log_stream, out_stream = run(args)
    with open(files[x_def_name], "r") as f:
        content = f.read()
    assert out_stream.getvalue().rstrip() == content.rstrip()

FN = collections.namedtuple('FN', ('name', 'protocol', 'hints'))

_i_data = [
    FN(name="x.zirkon", protocol="zirkon", hints=''),
    FN(name="x.json", protocol="json", hints=''),
    FN(name="x.json", protocol="json", hints=":json"),
    FN(name="xwrong.zirkon", protocol="json", hints=":json:config"),
]

_o_data = [
    FN(name="out_x.json", protocol="json", hints=''),
    FN(name="out_x.json", protocol="configobj", hints=":configobj"),
    FN(name="out_x.no_protocol", protocol=None, hints=''),
    FN(name="pickle/out_x.pickle", protocol="pickle", hints=''),
    FN(name="", protocol=None, hints=''),
    FN(name="", protocol="configobj", hints=":configobj"),
]

_s_data = [
    FN(name=None, protocol=None, hints=None),
    #FN(name="x.zirkon-schema", protocol="zirkon", hints=''),
    FN(name="x.s-json", protocol="json", hints=''),
]

_v_data = [
    FN(name=None, protocol=None, hints=None),
    FN(name="out_v.json-validation", protocol="json", hints=''),
    #FN(name="out_v.zirkon-validation", protocol="zirkon", hints=''),
]

@pytest.fixture(params=_i_data)
def i_name_protocol(request):
    return request.param

@pytest.fixture(params=_o_data)
def o_name_protocol(request):
    return request.param

@pytest.fixture(params=_s_data)
def s_name_protocol(request):
    return request.param

@pytest.fixture(params=_v_data)
def v_name_protocol(request):
    return request.param

@pytest.fixture(params=[None, True, False])
def defaults(request):
    return request.param

def test_main_list(files):
    fpaths = []
    for fname, fpath in files.items():
        fpaths.append(fpath)
    
    log_stream, out_stream = run(["list"])

    out_fpaths = {}
    for count, line in enumerate(out_stream.getvalue().split('\n')):
        if not line.strip():
            continue
        line_l = line.split()
        if count == 0:
            assert line_l[0] == "filename"
        elif count == 1:
            assert line_l[0][:len("filename")] == "--------"
        else:
            out_fpaths[line_l[0]] = (line_l[1], line_l[2])

    assert set(fpaths) == set(out_fpaths)
            
def test_main_read_write(files, i_name_protocol, o_name_protocol, s_name_protocol, v_name_protocol, defaults):
    i_name, i_protocol, i_hints = i_name_protocol
    o_name, o_protocol, o_hints = o_name_protocol
    s_name, s_protocol, s_hints = s_name_protocol
    v_name, v_protocol, v_hints = v_name_protocol

    if o_protocol is None:
        o_protocol = i_protocol
    with files.tmp(o_name), files.tmp(v_name):
        i_file_arg = files[i_name] + i_hints
        o_file_arg = files[o_name] + o_hints

        if o_name:
            assert not os.path.exists(files[o_name])
        if v_name:
            assert not os.path.exists(files[v_name])

        args = ["read", "-i", i_file_arg, "-o", o_file_arg]
        if s_name is not None:
            args.extend(["-s", s_name + s_hints])
            if v_name is not None:
                args.extend(["-V", v_name + v_hints])
        if defaults is not None:
            args.append("--defaults={!r}".format(defaults))
        log_stream, out_stream = run(args)

        if o_name:
            assert os.path.exists(files[o_name])

        config_args = {}
        if defaults is not None:
            config_args['defaults'] = defaults

        print("read in {}:{}".format(files[i_name], i_protocol))
        i_config = Config.from_file(files[i_name], protocol=i_protocol, **config_args)
        print("read out {}:{}".format(files[o_name], o_protocol))

        schema = None
        if s_name is not None:
            schema = Schema.from_file(files[s_name], protocol=s_protocol)
            validation = schema.validate(i_config)
            if v_name is not None:
                assert os.path.exists(v_name)
                v_data = Validation.from_file(files[v_name], protocol=v_protocol)
                print("===")
                validation.dump()
                print("===")
                v_data.dump()
                assert validation.to_string(protocol="zirkon") == v_data.to_string(protocol="zirkon")

        if o_name:
            o_config = Config.from_file(files[o_name], protocol=o_protocol, **config_args)
        else:
            o_config = Config.from_string(out_stream.getvalue(), protocol=o_protocol, **config_args)
        if schema:
            o_v_data = schema.validate(o_config)
            
        assert i_config == o_config
        out_x_json_path = files[o_name]
    assert not o_name in files
    assert not os.path.exists(out_x_json_path)
    
