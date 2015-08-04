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

from common.fixtures import simple_container, \
                            simple_config_content, \
                            simple_section, \
                            string_io, \
                            SIMPLE_SECTION_DUMP, \
                            SIMPLE_SECTION_REPR, \
                            SIMPLE_SECTION_STR

from daikon.section import Section

def test_Section_create(simple_container, string_io):
    section = Section(container=simple_container)
    section.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_Section_create_init(simple_container, simple_config_content, string_io):
    section = Section(container=simple_container, init=simple_config_content)
    section.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SECTION_DUMP

def test_Section_create_prefix(simple_container, simple_config_content, string_io):
    section = Section(container=simple_container, init=simple_config_content)
    options = Section(container=simple_container, prefix='options.')
    assert section['options'] == options

def test_Section_update(simple_container, simple_config_content, string_io):
    section = Section(container=simple_container)
    section.update(simple_config_content)
    section.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SECTION_DUMP

def test_Section_is_mapping(simple_section):
    assert isinstance(simple_section, collections.Mapping)

def test_Section_str(simple_section):
    assert str(simple_section) == SIMPLE_SECTION_STR

def test_Section_repr(simple_section):
    assert repr(simple_section) == SIMPLE_SECTION_REPR

def test_Section_unrepr(simple_section):
    section = eval(repr(simple_section), {'Section': Section, 'OrderedDict': collections.OrderedDict})
    assert section is not simple_section
    assert section == simple_section
def test_Section_has_parameter(simple_section):
    assert simple_section.has_parameter('x_value')
    assert not simple_section.has_parameter('w_value')
    assert not simple_section.has_parameter('options')

def test_Section_has_section(simple_section):
    assert not simple_section.has_section('x_value')
    assert not simple_section.has_section('w_section')
    assert simple_section.has_section('options')

def test_Section_getitem_parameter(simple_section):
    assert simple_section['y_value'] == 20.2
    assert simple_section['options']['i_alpha'] == 100
    assert simple_section['options']['epsilon']['epsilon_z'] == 30

def test_Section_getitem_section(simple_section, string_io):
    epsilon = simple_section['options']['epsilon']
    assert isinstance(epsilon, Section)
    epsilon.dump(stream=string_io)
    assert string_io.getvalue() == """\
epsilon_x = 10
epsilon_y = 20
epsilon_z = 30
"""

def test_Section_get_parameter(simple_section):
    assert simple_section.get_parameter('y_value') == 20.2
    with pytest.raises(KeyError) as exc_info:
        simple_section.get_parameter('options')

def test_Section_get_section(simple_section):
    options = simple_section.get_section('options')
    assert isinstance(options, Section)
    assert options['i_alpha'] == 100
    with pytest.raises(KeyError) as exc_info:
        simple_section.get_section('z_value')

def test_Section_setitem_parameter(simple_section):
    simple_section['xxx'] = 100
    assert simple_section.has_parameter('xxx')
    assert simple_section['xxx'] == 100
    simple_section['options']['yyy'] = 200
    assert simple_section['options'].has_parameter('yyy')
    assert simple_section['options']['yyy'] == 200

def test_Section_setitem_section(simple_section):
    simple_section['xxx'] = {'xx': 11}
    assert simple_section.has_section('xxx')
    assert simple_section['xxx'].has_parameter('xx')
    assert simple_section['xxx']['xx'] == 11

def test_Section_setitem_parameter_raises(simple_section):
    with pytest.raises(KeyError) as exc_info:
        simple_section['options'] = 100

def test_Section_setitem_section_raises(simple_section):
    with pytest.raises(KeyError) as exc_info:
        simple_section['x_value'] = {'y': 2}

def test_Section_delitem_section(simple_section):
    assert simple_section.has_section('options')
    del simple_section['options']
    assert not simple_section.has_section('options')
    simple_section['options'] = 123
    assert simple_section.has_parameter('options')
    assert simple_section['options'] == 123

def test_Section_delitem_parameter(simple_section):
    assert simple_section.has_parameter('y_value')
    del simple_section['y_value']
    assert not simple_section.has_parameter('y_value')
    simple_section['y_value'] = {'yy': 22}
    assert simple_section.has_section('y_value')
    assert simple_section['y_value']['yy'] == 22

def test_Section_parameters(simple_section):
    l = list(simple_section.parameters())
    assert l[0] == ('x_value', 10.1)
    assert l[1] == ('y_value', 20.2)
    assert l[2] == ('z_value', 30.3)

def test_Section_sections(simple_section):
    l = list(simple_section.sections())
    assert l[0][0] == 'options'
    assert isinstance(l[0][1], Section)
    assert l[0][1]['i_alpha'] == 100

    assert l[1][0] == 'miscellanea'
    assert isinstance(l[1][1], Section)
    assert l[1][1]['a'] == 1
    
def test_Section_items(simple_section):
    l = list(simple_section.items())
    assert l[0] == ('x_value', 10.1)
    assert l[1] == ('y_value', 20.2)
    assert l[2][0] == 'options'
    assert l[3] == ('z_value', 30.3)
    assert l[4][0] == 'miscellanea'

def test_Section_keys(simple_section):
    l = list(simple_section.keys())
    assert l[0] == 'x_value'
    assert l[1] == 'y_value'
    assert l[2] == 'options'
    assert l[3] == 'z_value'
    assert l[4] == 'miscellanea'

def test_Section_values(simple_section):
    l = list(simple_section.values())
    assert l[0] == 10.1
    assert l[1] == 20.2
    assert l[2]['i_alpha'] == 100
    assert l[3] == 30.3
    assert l[4]['b'] == 2

def test_Section_bad_key(simple_section):
    with pytest.raises(TypeError):
        simple_section[10] = 'ten'
    with pytest.raises(ValueError):
        simple_section["x.y"] = 'ten'
    with pytest.raises(ValueError):
        simple_section["x%y"] = 'ten'
    with pytest.raises(ValueError):
        simple_section["6y"] = 'ten'

def test_Section_bad_value(simple_section):
    with pytest.raises(TypeError):
        simple_section['w'] = lambda x: x * 2
    with pytest.raises(TypeError):
        simple_section['w'] = 4 + 3j

def test_Section_as_dict(simple_section):
    d = simple_section.as_dict()
    assert isinstance(d, collections.OrderedDict)
    assert d['x_value'] == 10.1
    assert d['y_value'] == 20.2
    assert isinstance(d['options'], collections.OrderedDict)
    assert d['options']['i_alpha'] == 100
    assert d['options']['f_beta'] == -0.123
    assert d['options']['b_gamma'] == True
    assert isinstance(d['options']['epsilon'], collections.OrderedDict)
    assert d['options']['epsilon']['epsilon_x'] == 10
    assert d['options']['epsilon']['epsilon_y'] == 20
    assert d['options']['epsilon']['epsilon_z'] == 30
    assert d['options']['s_delta'] == 'delta.dat'
    assert d['z_value'] == 30.3
def test_Section_eq_fast(simple_section):
    s0 = simple_section['options']
    assert s0 == Section(simple_section.container, prefix='options.')
    assert s0 != Section(simple_section.container, prefix='miscellanea.')

def test_Section_eq_slow(simple_section):
    s0 = Section(collections.OrderedDict(), init=simple_section)
    assert s0 == simple_section

def test_Section_eq_dict(simple_section):
    d = simple_section.as_dict()
    assert simple_section == d
    assert d == simple_section

def test_Section_ne_0(simple_section):
    s0 = Section(collections.OrderedDict(), init=simple_section)
    simple_section['options']['f'] = {'a': 1}
    assert s0 != simple_section
    assert simple_section != s0

def test_Section_ne_1(simple_section):
    s0 = Section(collections.OrderedDict(), init=simple_section)
    simple_section['options']['f'] = 34
    assert simple_section != s0
    assert s0 != simple_section

def test_Section_len_empty(simple_container):
    assert len(simple_container) == 0
    section = Section(container=simple_container)
    assert len(section) == 0
    assert len(simple_container) == 0
    section['a'] = 10
    assert len(section) == 1
    assert len(simple_container) == 1
    section['b'] = {'x': 0, 'y': 1, 'z': 2}
    assert len(section) == 2
    assert len(section['b']) == 3
    assert len(simple_container) == 1 + 1 + 3

def test_Section_len_simple_section(simple_section):
    assert len(simple_section) == 2 + 1 + 1 + 1
