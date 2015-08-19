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

import pytest

from common.fixtures import string_io

from zirkon.schema import Schema
from zirkon.config import ROOT, SECTION, Config
from zirkon.validator import Int, Float, Str
from zirkon.toolbox.deferred import Deferred
from zirkon.utils import create_template_from_schema, replace_deferred, \
    get_key, set_key, del_key

def test_create_template_from_schema(string_io):
    schema = Schema()
    schema['m0'] = Int(default=3)
    schema['m1'] = Int()
    schema['alpha'] = Float(default=0.5)
    schema['input_file'] = Str(min_len=1)
    schema['data'] = {}
    schema['data']['i'] = Int(max=10)
    schema['data']['isub'] = {}
    schema['data']['isub']['a'] = Str()
    schema['data']['isub']['b'] = Str(default='bc')
    schema['data']['isub']['c'] = Str(default=SECTION['b'] * ROOT['m0'])
    schema['data']['isub']['d'] = Str(default=SECTION['b'] * ROOT['m1'])
    schema['data']['j'] = Int(default=2)
    config = create_template_from_schema(schema)
    config.dump(stream=string_io)
    assert string_io.getvalue() == """\
m0 = 3
m1 = '# Int()'
alpha = 0.5
input_file = '# Str(min_len=1)'
[data]
    i = '# Int(max=10)'
    [isub]
        a = '# Str()'
        b = 'bc'
        c = SECTION['b'] * ROOT['m0']
        d = SECTION['b'] * ROOT['m1']
    j = 2
"""

def test_create_template_from_schema(string_io):
    schema = Schema()
    schema['m0'] = Int(default=3)
    schema['m1'] = Int(default=ROOT['m0'] + 1)
    config = Config()
    create_template_from_schema(schema, config=config)
    
    config.dump(stream=string_io)
    assert string_io.getvalue() == """\
m0 = 3
m1 = ROOT['m0'] + 1
"""

def test_replace_deferred():
    a_value = 10
    c_value = 5
    x_value = 4
    z_value = 7
    config1 = Config(defaults=True)
    config2 = Config(defaults=True)
    for config in config1, config2:
        config['a'] = a_value
        config['b'] = 2 * ROOT['a']
        config['sub'] = {}
        config['sub']['x'] = x_value
        config['sub']['y'] = SECTION['x'] + ROOT['b']
        config.set_defaults(c=c_value, d=3 + ROOT['c'] + SECTION['a'],
                            sub={'z': z_value,
                                 'subsub': {'t': ROOT['a'] - 1},
                                 'w': SECTION['x'] + SECTION['z'] + ROOT['a'] + ROOT['c']})


    def verify(cnfg, a_value, c_value, x_value, z_value, def_a_value=None):
        if def_a_value is None:
            def_a_value = a_value
        assert cnfg['a'] == a_value
        assert cnfg['b'] == 2 * def_a_value
        assert cnfg['sub']['x'] == x_value
        assert cnfg['sub']['y'] == x_value + (2 * def_a_value)
        assert cnfg['sub']['z'] == z_value
        assert cnfg['sub']['w'] == x_value + z_value + def_a_value + c_value
        assert cnfg['c'] == c_value
        assert cnfg['d'] == 3 + c_value + def_a_value

    verify(config1, a_value, c_value, x_value, z_value)
    verify(config2, a_value, c_value, x_value, z_value)

    a_value = 100
    config1['a'] = a_value
    config2['a'] = a_value
    verify(config1, a_value, c_value, x_value, z_value)
    verify(config2, a_value, c_value, x_value, z_value)

    replace_deferred(config2)

    new_a_value1 = 67
    config1['a'] = new_a_value1
    config2['a'] = new_a_value1
    verify(config1, new_a_value1, c_value, x_value, z_value)
    verify(config2, new_a_value1, c_value, x_value, z_value, def_a_value=a_value)

    replace_deferred(config1)

    new_a_value2 = 67
    config1['a'] = new_a_value2
    config2['a'] = new_a_value2
    verify(config1, new_a_value2, c_value, x_value, z_value, def_a_value=new_a_value1)
    verify(config2, new_a_value2, c_value, x_value, z_value, def_a_value=a_value)

def test_get_key():
    config = Config()
    config['x'] = 10
    config['sub'] = {'y': 20}
    config['sub']['sub'] = {'z': 30}
    
    assert get_key(config, "x") == 10
    assert get_key(config, "sub.y") == 20
    assert get_key(config, ("sub", "y")) == 20
    assert get_key(config, "sub.sub.z") == 30
    assert get_key(config, ("sub", "sub", "z")) == 30
    assert get_key(config, ()) == config
    with pytest.raises(KeyError) as exc_info:
        get_key(config, "y")
    assert str(exc_info.value) == "'y'"

def test_set_key(string_io):
    config = Config()
    with pytest.raises(KeyError) as exc_info:
        set_key(config, (), 3)
    assert str(exc_info.value) == "()"

    with pytest.raises(KeyError) as exc_info:
        set_key(config, "", 3)
    assert str(exc_info.value) == "''"

    set_key(config, "x", 10)
    set_key(config, "sub", {'y': 20})
    set_key(config, "sub.z", 30)
    with pytest.raises(KeyError) as exc_info:
        set_key(config, "sub.sub2.w", 40)
    assert str(exc_info.value) == "'sub2'"
    set_key(config, "sub.sub2.w", 40, parents=True)

    config.dump(string_io)
    assert string_io.getvalue() == """\
x = 10
[sub]
    y = 20
    z = 30
    [sub2]
        w = 40
"""

def test_del_key(string_io):
    config = Config()
    config['x'] = 10
    config['sub'] = {'y': 20}
    config['sub']['sub1'] = {'z': 30, 'w': 40}
    config['sub']['sub2'] = {'z': 30, 'w': 40}

    del_key(config, "x")
    with pytest.raises(KeyError) as exc_info:
        del_key(config, "x")
    assert str(exc_info.value) == "'x'"
    del_key(config, "x", ignore_errors=True)

    with pytest.raises(KeyError) as exc_info:
        del_key(config, "sub.sub3.xx")
    assert str(exc_info.value) == "'sub3'"
    
    del_key(config, "sub.sub1")
    del_key(config, "sub.sub2.z")
    config.dump(string_io)
    assert string_io.getvalue() == """\
[sub]
    y = 20
    [sub2]
        w = 40
"""
