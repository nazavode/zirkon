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

from common.fixtures import dictionary, \
                            generic_dictionary, \
                            simple_config_content, \
                            simple_section, \
                            string_io, \
                            SIMPLE_SECTION_DUMP, \
                            SIMPLE_SECTION_REPR, \
                            SIMPLE_SECTION_STR

from daikon.section import Section

def test_Section_create(generic_dictionary, string_io):
    section = Section(dictionary=generic_dictionary)
    section.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_Section_create_init(dictionary, simple_config_content, string_io):
    section = Section(dictionary=dictionary, init=simple_config_content)
    section.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SECTION_DUMP

def test_Section_update(dictionary, simple_config_content, string_io):
    section = Section(dictionary=dictionary)
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

def test_Section_has_option(simple_section):
    assert simple_section.has_option('x_value')
    assert not simple_section.has_option('w_value')
    assert not simple_section.has_option('options')

def test_Section_has_section(simple_section):
    assert not simple_section.has_section('x_value')
    assert not simple_section.has_section('w_section')
    assert simple_section.has_section('options')

def test_Section_has_key(simple_section):
    assert simple_section.has_key('x_value')
    assert not simple_section.has_key('w_section')
    assert simple_section.has_key('options')

def test_Section_getitem_option(simple_section):
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

def test_Section_get_option(simple_section):
    assert simple_section.get_option('y_value') == 20.2
    with pytest.raises(KeyError) as exc_info:
        simple_section.get_option('options')

def test_Section_get_section(simple_section):
    options = simple_section.get_section('options')
    assert isinstance(options, Section)
    assert options['i_alpha'] == 100
    with pytest.raises(KeyError) as exc_info:
        simple_section.get_section('z_value')

def test_Section_setitem_option(simple_section):
    simple_section['xxx'] = 100
    assert simple_section.has_option('xxx')
    assert simple_section['xxx'] == 100
    simple_section['options']['yyy'] = 200
    assert simple_section['options'].has_option('yyy')
    assert simple_section['options']['yyy'] == 200

def test_Section_setitem_section(simple_section):
    simple_section['xxx'] = {'xx': 11}
    assert simple_section.has_section('xxx')
    assert simple_section['xxx'].has_option('xx')
    assert simple_section['xxx']['xx'] == 11

def test_Section_setitem_option_raises(simple_section):
    with pytest.raises(TypeError) as exc_info:
        simple_section['options'] = 100

def test_Section_setitem_section_raises(simple_section):
    with pytest.raises(TypeError) as exc_info:
        simple_section['x_value'] = {'y': 2}

def test_Section_delitem_section(simple_section):
    assert simple_section.has_section('options')
    del simple_section['options']
    assert not simple_section.has_section('options')
    simple_section['options'] = 123
    assert simple_section.has_option('options')
    assert simple_section['options'] == 123

def test_Section_delitem_option(simple_section):
    assert simple_section.has_option('y_value')
    del simple_section['y_value']
    assert not simple_section.has_option('y_value')
    simple_section['y_value'] = {'yy': 22}
    assert simple_section.has_section('y_value')
    assert simple_section['y_value']['yy'] == 22

def test_Section_options(simple_section):
    l = list(simple_section.options())
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
    assert simple_section == Section(dictionary=simple_section.dictionary)

def test_Section_eq_slow(simple_section):
    s0 = Section(init=simple_section)
    assert s0 == simple_section

def test_Section_eq_dict(simple_section):
    d = simple_section.as_dict()
    assert simple_section == d
    assert d == simple_section

def test_Section_ne_0(simple_section):
    s0 = Section(init=simple_section)
    simple_section['options']['f'] = {'a': 1}
    simple_section.dump()
    assert s0 != simple_section
    assert simple_section != s0

def test_Section_ne_1(simple_section):
    s0 = Section(init=simple_section)
    simple_section['options']['f'] = 34
    simple_section.dump()
    assert simple_section != s0
    assert s0 != simple_section

def test_Section_len_empty(generic_dictionary):
    section = Section(dictionary=generic_dictionary)
    assert len(section) == 0
    section['a'] = 10
    assert len(section) == 1
    section['b'] = {'x': 0, 'y': 1, 'z': 2}
    assert len(section) == 2
    assert len(section['b']) == 3

def test_Section_len_simple_section(simple_section):
    assert len(simple_section) == 2 + 1 + 1 + 1

def test_Section_add_section(simple_section):
    assert not 'xyz' in simple_section
    assert not simple_section.has_section('xyz')
    section = simple_section.add_section('xyz')
    assert 'xyz' in simple_section
    assert section == simple_section['xyz']
    assert len(simple_section['xyz']) == 0
    section['a'] = 10
    assert len(simple_section['xyz']) == 1
    assert section == simple_section['xyz']

def test_Section_invalid_list_content():
    section = Section()
    with pytest.raises(TypeError) as exc_info:
        section['a'] = (1, 23, {})
    assert str(exc_info.value) == "option a: invalid tuple: item #2 {} has invalid type dict"

def test_Section_invalid_dictionary_content():
    dictionary = {'a': (1, 23, {}), 'b': 8}
    section = Section(dictionary=dictionary)
    assert section['b'] == 8
    with pytest.raises(TypeError) as exc_info:
        a = section['a']
    assert str(exc_info.value) == "option a: invalid tuple: item #2 {} has invalid type dict"

def test_Section_defaults():
    dictionary = collections.OrderedDict()
    section = Section(dictionary=dictionary)
    section.add_default(alpha=10)
    assert 'alpha' in section
    assert section['alpha'] == 10
    assert len(tuple(section.keys())) == 0
    assert len(tuple(section.options())) == 0
    assert len(tuple(section.defaults())) == 1
    assert len(tuple(section.options(defaults=True))) == 1
    assert len(dictionary) == 0
    section['alpha'] = 20
    assert section['alpha'] == 20
    assert len(tuple(section.keys())) == 1
    assert len(tuple(section.options())) == 1
    assert len(tuple(section.defaults())) == 0
    assert len(section._defaults) == 1
    assert len(tuple(section.options(defaults=True))) == 1
    assert len(dictionary) == 1
    del section['alpha']
    assert section['alpha'] == 10
    
def test_Section_defaults_external():
    defaults = Section(defaults=False)
    defaults['a'] = 10
    defaults['sa'] = {'x': 1}
    section = Section(defaults=defaults)
    section.add_default(b=20, sb={'y': 2})
    for sec in defaults, section:
        assert sec.has_option('a')
        assert sec['a'] == 10
        assert sec.has_section('sa')
        assert sec['sa'].has_option('x')
        assert sec['sa']['x'] == 1
        assert sec.has_option('b')
        assert sec['b'] == 20
        assert sec.has_section('sb')
        assert sec['sb'].has_option('y')
        assert sec['sb']['y'] == 2
    #assert defaults == section

def test_Section_no_defaults_add_default():
    section = Section(defaults=False)
    section.add_default(alpha=10, beta={'x': 1})
    assert section.has_option('alpha')
    assert section['alpha'] == 10
    assert len(section) == 2
    assert section.has_section('beta')
    assert section['beta'].has_option('x')
    assert section['beta']['x'] == 1
    assert len(section['beta']) == 1

def test_Section_get_defaults():
    section = Section(defaults=True)
    defaults = section.get_defaults()
    assert isinstance(defaults, Section)

def test_Section_get_defaults_None():
    section = Section(defaults=False)
    defaults = section.get_defaults()
    assert defaults is None

def test_Section_defaults_subsection():
    dictionary = collections.OrderedDict()
    section = Section(dictionary=dictionary)
    section.add_default(epsilon={'eps': 0.01})
    assert section.has_section('epsilon')
    assert section['epsilon'].has_option('eps')
    assert section['epsilon']['eps'] == 0.01
    assert len(section) == 0
    assert len(dictionary) == 0

def test_Section_defaults_update():
    section = Section()
    section.add_default(alpha=10)
    section.add_default(beta=5, epsilon={'eps': 0.01})
    section2 = Section()
    section2['alpha'] = 20
    section2.update(section)
    assert section2['alpha'] == 20
    assert section2['beta'] == 5
    del section2['alpha']
    assert section2['alpha'] == 10
    
def test_Section_defaults_dump(string_io):
    section = Section()
    section['x'] = 1
    section.add_default(alpha=10)
    section['sub'] = {'w': 2}
    section['sub'].add_default(beta=20)
    assert section['sub']['beta'] == 20
    section.dump(string_io)
    assert string_io.getvalue() == """\
x = 1
[sub]
    w = 2
"""

def test_Section_defaults_sub():
    section = Section()
    section.add_default(a=10, sub={'x': 1, 'subsub': {'xx': 11, 'subsubsub': {'xxx': 111, 'yyy': 222}, 'yy': 22}, 'y': 2}, b=20)
    assert section['a'] == 10
    assert section['sub']['x'] == 1
    assert section['sub']['subsub']['xx'] == 11
    assert section['sub']['subsub']['subsubsub']['xxx'] == 111
    assert section['sub']['subsub']['subsubsub']['yyy'] == 222
    assert section['sub']['subsub']['yy'] == 22
    assert section['sub']['y'] == 2
    assert section['b'] == 20

def test_Section_defaults_sub():
    section = Section()
    section['a'] = 10
    section['sub'] = {}
    section['sub']['x'] = 1
    section['sub']['subsub'] = {}
    section['sub']['subsub']['xx'] = 11
    section['sub']['subsub']['subsubsub'] = {}
    section['sub']['subsub']['subsubsub']['xxx'] = 111
    section['sub']['subsub']['subsubsub']['yyy'] = 222
    section['sub']['subsub']['yy'] = 22
    section['sub']['y'] = 2
    section['b'] = 20
    section2 = Section()
    section2.add_default(**section)

    assert section2['a'] == 10
    assert section2['sub']['x'] == 1
    assert section2['sub']['subsub']['xx'] == 11
    assert section2['sub']['subsub']['subsubsub']['xxx'] == 111
    assert section2['sub']['subsub']['subsubsub']['yyy'] == 222
    assert section2['sub']['subsub']['yy'] == 22
    assert section2['sub']['y'] == 2
    assert section2['b'] == 20
    assert len(section2) == 0
    assert section2.has_option('a')
    assert section2.has_section('sub')

@pytest.fixture
def s_option():
    section = Section()
    section.add_default(a=10, b=20)
    section['a'] = 5
    section['c'] = 15
    return section

def test_Section_defaults_deloption_loc_def(s_option):
    section = s_option
    assert section.has_key('a')
    assert section.has_option('a')
    del section['a']
    assert section.has_key('a')
    assert section.has_option('a')

def test_Section_defaults_deloption_only_def(s_option):
    section = s_option
    assert section.has_key('b')
    assert section.has_option('b')
    with pytest.raises(KeyError) as exc_info:
        del section['b']
    assert section.has_key('b')
    assert section.has_option('b')

def test_Section_defaults_deloption_only_loc(s_option):
    section = s_option
    assert section.has_key('c')
    assert section.has_option('c')
    del section['c']
    assert not section.has_key('c')
    assert not section.has_option('c')

@pytest.fixture
def s_section():
    section = Section()
    section.add_default(a={'ax': 1}, b={'bx': 2})
    section['a'] = {'ax': 10}
    section['c'] = {'cx': 20}
    return section

def test_Section_defaults_delsection_loc_def(s_section):
    section = s_section
    assert section.has_key('a')
    assert section.has_section('a')
    del section['a']
    assert section.has_key('a')
    assert section.has_section('a')

def test_Section_defaults_delsection_only_def(s_section):
    section = s_section
    assert section.has_key('b')
    assert section.has_section('b')
    with pytest.raises(KeyError) as exc_info:
        del section['b']
    assert section.has_key('b')
    assert section.has_section('b')

def test_Section_defaults_delsection_only_loc(s_section):
    section = s_section
    assert section.has_key('c')
    assert section.has_section('c')
    del section['c']
    section._defaults.dump()
    assert not section.has_key('c')
    assert not section.has_section('c')

