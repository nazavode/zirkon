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
    protocol, \
    defaultsvalue, \
    generic_dictionary, \
    simple_config_content, \
    simple_config, \
    string_io, \
    tmp_text_file, \
    SIMPLE_SECTION_DUMP, \
    SIMPLE_CONFIG_JSON_SERIALIZATION, \
    SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION, \
    SIMPLE_CONFIG_ZIRKON_SERIALIZATION

from zirkon.toolbox.deferred import Deferred
from zirkon.toolbox.dictutils import compare_dicts, as_dict
from zirkon.section import Section
from zirkon.defaults_section import DefaultsSection
from zirkon.config_section import ConfigSection
from zirkon.config import Config, ROOT, SECTION
from zirkon.toolbox.serializer import JSONSerializer, \
    ConfigObjSerializer, PickleSerializer

def test_Config_create_empty(string_io, defaultsvalue):
    config = Config(defaults=defaultsvalue)
    config.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_Config_create_dictionary(generic_dictionary, string_io, defaultsvalue):
    config = Config(dictionary=generic_dictionary, defaults=defaultsvalue)
    config.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_Config_create_init(simple_config_content, string_io, defaultsvalue):
    config = Config(init=simple_config_content, defaults=defaultsvalue)
    config.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SECTION_DUMP

def test_Config_create_dictionary_init(dictionary, simple_config_content, string_io, defaultsvalue):
    config = Config(dictionary=dictionary, init=simple_config_content, defaults=defaultsvalue)
    config.dump(stream=string_io)
    assert string_io.getvalue() == SIMPLE_SECTION_DUMP
    assert len(dictionary) > 0

def test_Config_create_dictionary_init_overlap(string_io, defaultsvalue):
    dictionary = collections.OrderedDict()
    dictionary['x'] = 10
    dictionary['y'] = 10
    init = {'a': 20, 'y': 30}
    config = Config(init, dictionary=dictionary, defaults=defaultsvalue)
    assert len(config) == 3
    assert config['x'] == 10
    assert config['y'] == 30
    assert config['a'] == 20

def test_Config_to_file_json(simple_config, tmp_text_file):
    simple_config.to_file(filename=tmp_text_file.name, protocol="json")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_CONFIG_JSON_SERIALIZATION

def test_Config_from_file_json(simple_config, tmp_text_file):
    tmp_text_file.write(SIMPLE_CONFIG_JSON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    config = Config.from_file(filename=tmp_text_file.name, protocol="json")
    assert config == simple_config

def test_Config_to_file_configobj(simple_config, tmp_text_file):
    simple_config.to_file(filename=tmp_text_file.name, protocol="configobj")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION

def test_Config_from_file_configobj(simple_config, tmp_text_file):
    tmp_text_file.write(SIMPLE_CONFIG_CONFIGOBJ_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    config = Config.from_file(filename=tmp_text_file.name, protocol="configobj")
    assert config == simple_config

def test_Config_to_file_zirkon(simple_config, tmp_text_file):
    simple_config.to_file(filename=tmp_text_file.name, protocol="zirkon")
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    serialization = tmp_text_file.read()
    assert serialization == SIMPLE_CONFIG_ZIRKON_SERIALIZATION

def test_Config_from_file_zirkon(simple_config, tmp_text_file):
    tmp_text_file.write(SIMPLE_CONFIG_ZIRKON_SERIALIZATION)
    tmp_text_file.flush()
    tmp_text_file.seek(0)
    config = Config.from_file(filename=tmp_text_file.name, protocol="zirkon")
    assert config == simple_config

def test_Config_get_serializer_json():
    assert isinstance(Config.get_serializer("json"), JSONSerializer)

def test_Config_get_serializer_configobj():
    assert isinstance(Config.get_serializer("configobj"), ConfigObjSerializer)

def test_Config_get_serializer_pickle():
    assert isinstance(Config.get_serializer("pickle"), PickleSerializer)

def test_Config_deferred(defaultsvalue):
    config = Config(defaults=defaultsvalue)
    config['a'] = 10
    config['b'] = 20
    config['c'] = SECTION['a'] * SECTION['b']
    config['sub'] = {}
    config['sub']['x'] = 7
    config['options'] = {}
    config['options']['d'] = 100
    config['options']['e'] = ROOT['a'] + ROOT['sub']['x'] + SECTION['d']

    assert isinstance(config['c'], int)
    assert config['c'] == 200
    assert isinstance(config['options']['e'], int)
    assert config['options']['e'] == 117

    config['a'] += 10

    assert config['c'] == 400
    assert config['options']['e'] == 127

def test_Config_deferred_error(defaultsvalue):
    config = Config(defaults=defaultsvalue)
    config['a'] = 10
    config['c'] = SECTION['a'] * SECTION['b']
    with pytest.raises(KeyError) as exc_info:
        x = config['c']
    assert str(exc_info.value) == "'b'"

def test_Config_defaults_option():
    config = Config(defaults=True)
    config.set_defaults(a=10)
    assert 'a' in config
    assert config.has_key('a')
    assert config.has_option('a')
    assert config['a'] == 10
    assert config.get('a') == 10
    assert config.get_option('a') == 10
    assert len(config) == 0
    assert not 'a' in config.dictionary

def test_Config_defaults_section():
    config = Config(defaults=True)
    config.set_defaults(a={'x': 1})
    assert 'a' in config
    assert config.has_key('a')
    assert config.has_section('a')
    assert isinstance(config['a'], Section)
    assert len(config) == 1
    assert len(config['a']) == 0
    assert config['a'].has_option('x')
    assert config.get('a') == config['a']
    assert config.get_section('a') == config['a']
    config['a'] = {'y': 2}
    assert len(config['a']) == 1
    assert config['a'].has_option('x')
    assert config['a'].has_option('y')
    del config['a']
    assert config.has_section('a')
    assert len(config['a']) == 0
    assert config['a'].has_option('x')
    #config['x'] = {}
    #assert config.has_section('x')
    #del config['x']
    #assert not config.has_section('x')

def test_Config_defaults_Config():
    defaults = Config()
    defaults["y"] = ROOT["x"] * 10
    config1 = Config(defaults=defaults)
    config1["x"] = 3
    config2 = Config(defaults=defaults)
    config2["x"] = 7
    assert config1["y"] == 30
    assert config2["y"] == 70

def test_Config_defaults_section_add():
    config = Config(defaults=True)
    config.set_defaults(a={'x': 1})
    assert 'a' in config
    config['a']['t'] = 0.1
    assert config['a']['x'] == 1
    assert config['a']['t'] == 0.1
    assert not config.defaults['a'].has_option('t')
    del config['a']
    assert config.has_section('a')
    assert config['a'].has_option('x')
    assert config['a']['x'] == 1

def test_Config_defaults_add_overlap(defaultsvalue):
    config = Config(defaults=defaultsvalue)
    config['a'] = 100
    config['b'] = 101
    config['sub'] = {}
    config['sub']['x'] = 10
    config['sub']['y'] = 11
    config.set_defaults(b=201, c=202, sub={'y': 21, 'z': 22})
    assert 'a' in config
    assert config['a'] == 100
    assert 'b' in config
    assert config['b'] == 101
    assert 'c' in config
    assert config['c'] == 202
    assert 'x' in config['sub']
    assert config['sub']['x'] == 10
    assert 'y' in config['sub']
    assert config['sub']['y'] == 11
    assert 'z' in config['sub']
    assert config['sub']['z'] == 22

def test_Config_defaults_add_subsub():
    config = Config(defaults=True)
    config['x'] = 10
    config.set_defaults(a=1, sub={'sa': 2, 'subsub': {'ssa': 3, 'empty1': {}, 'empty2': {'ee1': {}, 'ee2': {}}, 'subsubsub': {'sss': 4}, 'ssb': 5}, 'sb': 6}, b=7)
    assert config.has_section('sub')
    assert config['sub'].has_section('subsub')
    assert config['sub']['subsub'].has_section('subsubsub')
    assert not config['sub']['subsub'].has_section('empty1')
    assert not config['sub']['subsub'].has_section('empty2')

@pytest.fixture(params=[collections.OrderedDict(), Section(), Config()])
def extdefaults(request):
    defaults = request.param
    defaults['i10'] = 10
    defaults['sub'] = collections.OrderedDict()
    defaults['sub']['f11'] = 1.1
    defaults['sub']['f22'] = 2.2
    defaults['sub']['sse'] = collections.OrderedDict()
    defaults['sub']['ssf'] = collections.OrderedDict()
    defaults['sub']['ssf']['f44'] = 4.4
    defaults['xdat'] = "x.dat"
    return defaults

def test_Config_defaults_external(extdefaults):
    edcopy = as_dict(extdefaults, depth=-1, dict_class=dict)
    config = Config(defaults=extdefaults)
    assert config.has_section('sub')
    assert config['sub']['f22'] == 2.2
    assert not config['sub'].has_section('sse')
    with pytest.raises(KeyError) as exc_info:
        config['sub']['sse']['xx'] = 18
    assert str(exc_info.value) == "'sse'"
    assert not config['sub'].has_section('sse')
    assert config['sub'].has_section('ssf')
    assert len(config['sub']['ssf']) == 0
    assert config['sub']['ssf']['f44'] == 4.4
    config['sub']['ssf']['xx'] = 19
    del config['sub']
    assert config.has_section('sub')
    assert config['sub'].has_section('ssf')
    assert config['sub']['ssf'].has_option('f44')
    assert config['sub']['ssf']['f44'] == 4.4
    edcopy2 = as_dict(extdefaults, depth=-1, dict_class=dict)
    assert edcopy == edcopy2
    
def test_Config_no_defaults_set_defaults():
    config = Config(defaults=False)
    config.set_defaults(alpha=10, beta={'x': 1})
    assert config.has_option('alpha')
    assert config['alpha'] == 10
    assert len(config) == 2
    assert config.has_section('beta')
    assert config['beta'].has_option('x')
    assert config['beta']['x'] == 1
    assert len(config['beta']) == 1

def test_Config_defaults_get_defaults():
    config = Config(defaults=True)
    config.set_defaults(a={'x': 1}, b=10)
    assert isinstance(config.defaults, Section)
    assert config.defaults == {'a': {'x': 1}, 'b': 10}
    config = Config(defaults=False)
    assert config.defaults is None

def test_Config_defaults_empty_section():
    config = Config(defaults=True)
    config.set_defaults(a={})
    assert not 'a' in config
    assert not config.has_key('a')
    assert not config.has_section('a')

def test_Config_defaults_update(defaultsvalue):
    config1 = Config(defaults=defaultsvalue)
    config1['d'] = 11
    config1['e'] = 12
    config1.set_defaults(a={}, b=5, c={'x': 7}, d=8)
    config2 = Config(defaults=True)
    config2.update(config1)
    assert config2 == config1
    config1.set_defaults(only1=1)
    assert not config2.has_option('only1')
    config2.set_defaults(only2=2)
    assert not config1.has_option('only2')
    assert config2 != config1

def test_Config_copy(defaultsvalue):
    config = Config(defaults=defaultsvalue)
    config['a'] = 10
    config.set_defaults(b=20)
    config2 = config.copy()
    assert config2 == config

def test_Config_defaults_copy():
    config = Config(defaults=True)
    config['d'] = 11
    config['e'] = 12
    config.set_defaults(a={}, b=5, c={'x': 7}, d=8)
    config2 = config.copy()
    assert not config2.has_section('a')
    assert config2.has_option('b')
    assert config2['b'] == 5
    assert config2.has_section('c')
    assert len(config2['c']) == 0
    assert config2['c']['x'] == 7
    assert config2.has_option('d')
    assert config2['d'] == 11
    assert config2.has_option('e')
    assert config2['e'] == 12

def test_Config_defaults_dump(string_io):
    config = Config(defaults=True)
    config['x'] = 1
    config.set_defaults(alpha=10)
    config['sub'] = {'w': 2}
    config['sub'].set_defaults(beta=20, gamma={'x': 11}, delta={})
    assert config['sub']['beta'] == 20
    assert config['sub']['gamma']['x'] == 11
    config.dump(string_io)
    assert string_io.getvalue() == """\
x = 1
[sub]
    w = 2
    [gamma]
"""

def test_Config_defaults_sub():
    config = Config(defaults=True)
    config['a'] = 10
    config['sub'] = {}
    config['sub']['x'] = 1
    config['sub']['subsub'] = {}
    config['sub']['subsub']['xx'] = 11
    config['sub']['subsub']['subsubsub'] = {}
    config['sub']['subsub']['subsubsub']['xxx'] = 111
    config['sub']['subsub']['subsubsub']['yyy'] = 222
    config['sub']['subsub']['yy'] = 22
    config['sub']['y'] = 2
    config['b'] = 20

    config2 = Config(defaults=True)
    config2.set_defaults(**config)
    assert len(config2) == 0

    assert config2['a'] == 10
    assert config2['sub']['x'] == 1
    assert config2['sub']['subsub']['xx'] == 11
    assert config2['sub']['subsub']['subsubsub']['xxx'] == 111
    assert config2['sub']['subsub']['subsubsub']['yyy'] == 222
    assert config2['sub']['subsub']['yy'] == 22
    assert config2['sub']['y'] == 2
    assert config2['b'] == 20
    assert len(config2) == 1
    assert config2.has_option('a')
    assert config2.has_section('sub')

def test_Config_defaults_deloptions():
    config = Config(defaults=True)
    config['d'] = 11
    config['e'] = 12
    config.set_defaults(a={}, b=5, c={'x': 7}, d=8)
    assert config.has_option('d')
    assert config['d'] == 11
    del config['d']
    assert config.has_option('d')
    assert config['d'] == 8
    assert config.has_option('e')
    assert config['e'] == 12
    del config['e']
    assert not config.has_option('e')
    with pytest.raises(KeyError):
        del config['e']
    del config['d']
    assert config.has_option('d')
    del config['c']
    assert config.has_section('c')
    assert config['c']['x'] == 7

def test_Config_defaults_eq():
    config = Config(defaults=True)
    config['d'] = 11
    config['e'] = 12
    config.set_defaults(a={}, b=5, c={'x': 7}, d=8)
    
    config2 = Config(defaults=True)
    config2['d'] = 11
    config2['e'] = 12

    assert config != config2

@pytest.fixture
def config_option():
    config = Config(defaults=True)
    config.set_defaults(a=10, b=20)
    config['a'] = 5
    config['c'] = 15
    return config

def test_Config_defaults_deloption_loc_def(config_option):
    config = config_option
    assert config.has_key('a')
    assert config.has_option('a')
    assert config['a'] == 5
    del config['a']
    assert config.has_key('a')
    assert config.has_option('a')
    assert config['a'] == 10

def test_Config_defaults_deloption_only_def(config_option):
    config = config_option
    assert config.has_key('b')
    assert config.has_option('b')
    assert config['b'] == 20
    del config['b']
    assert config.has_key('b')
    assert config.has_option('b')
    assert config['b'] == 20

def test_Config_defaults_deloption_only_loc(config_option):
    config = config_option
    assert config.has_key('c')
    assert config.has_option('c')
    assert config['c'] == 15
    del config['c']
    assert not config.has_key('c')
    assert not config.has_option('c')

@pytest.fixture
def config_section():
    config = Config(defaults=True)
    config.set_defaults(a={'ax': 1}, b={'bx': 2})
    config['a'] = {'ax': 10}
    config['c'] = {'cx': 20}
    return config

def test_Config_defaults_delsection_loc_def(config_section):
    config = config_section
    assert config.has_key('a')
    assert config.has_section('a')
    assert config['a'] == {'ax': 10}
    del config['a']
    assert config.has_key('a')
    assert config.has_section('a')
    assert config['a'] == {'ax': 1}

def test_Config_defaults_delsection_only_def(config_section):
    config = config_section
    assert config.has_key('b')
    assert config.has_section('b')
    assert config['b'] == {'bx': 2}
    del config['b']
    assert config.has_key('b')
    assert config.has_section('b')
    assert config['b'] == {'bx': 2}

def test_Config_defaults_delsection_only_loc(config_section):
    config = config_section
    assert config.has_key('c')
    assert config.has_section('c')
    assert config['c'] == {'cx': 20}
    del config['c']
    config._defaults.dump()
    assert not config.has_key('c')
    assert not config.has_section('c')

@pytest.fixture
def defconfig(defaultsvalue):
    config = Config(defaults=defaultsvalue)
    config['n'] = 10
    config['sub'] = {}
    config['sub']['n0'] = 1
    config['sub']['n1'] = ROOT['n'] + SECTION['n0']
    config['sub']['sub'] = {}
    config['sub']['sub']['n2'] = ROOT['n'] * ROOT['sub']['n1']
    return config

def test_Config_deferred_protocol(defconfig, protocol):
    s_defconfig = defconfig.to_string(protocol=protocol)
    defconfig_reloaded = Config.from_string(s_defconfig, protocol=protocol)
    assert defconfig_reloaded == defconfig

def test_Config_deferred_dump(defconfig):
    s_defconfig = defconfig.to_string(protocol="zirkon")
    assert s_defconfig == """\
n = 10
[sub]
    n0 = 1
    n1 = ROOT['n'] + SECTION['n0']
    [sub]
        n2 = ROOT['n'] * ROOT['sub']['n1']
"""

def test_Config_deferred_copy(defconfig):
    config = defconfig.copy()
    assert isinstance(defconfig.dictionary['sub']['n1'], Deferred)
    assert isinstance(config.dictionary['sub']['n1'], Deferred)
    
def test_Config_deferred_defaults(defconfig):
    defconfig.set_defaults(a=ROOT['n'] - 3, sub={'b': ROOT['n'] - 7})
    assert defconfig['a'] == 7
    assert defconfig['sub']['b'] == 3
    config = defconfig.copy()
    assert config['a'] == 7
    assert config['sub']['b'] == 3
    defconfig['n'] = 20
    config['n'] = 110
    assert defconfig['a'] == 17
    assert defconfig['sub']['b'] == 13
    assert config['a'] == 107
    assert config['sub']['b'] == 103
     
def test_Config_deferred_as_dict_evaluate_False(defconfig):
    defconfig.set_defaults(a=ROOT['n'] - 3, sub={'b': ROOT['n'] - 7})
    dct = defconfig.as_dict(evaluate=False)
    assert isinstance(dct['sub']['n1'], Deferred)
    assert isinstance(dct['sub']['b'], Deferred)

def test_Config_deferred_as_dict(defconfig):
    defconfig.set_defaults(a=ROOT['n'] - 3, sub={'b': ROOT['n'] - 7})
    dct = defconfig.as_dict()
    assert isinstance(dct['sub']['n1'], int)
    assert dct['sub']['n1'] == 11
    assert 'b' in dct['sub']
    assert isinstance(dct['sub']['b'], int)
    assert dct['sub']['b'] == 3

def test_Config_shared_defaults():
    defaults = DefaultsSection()
    defaults['sub'] = {'x': ROOT['n'] * 3, 'sub': {'x': ROOT['n'] * 4}}
    defaults['x'] = 1000 + ROOT['n']
    config1 = Config(defaults=defaults)
    config1['n'] = 10
    config2 = Config(defaults=defaults)
    config2['n'] = 20
    assert config1['x'] == 1010
    assert config1['sub']['x'] == 30
    assert config1['sub']['sub']['x'] == 40
    assert config2['x'] == 1020
    assert config2['sub']['x'] == 60
    assert config2['sub']['sub']['x'] == 80

def test_Config_sub_setdef():
    config = Config(defaults={'sub': {'a': 100}})
    config['x'] = 10
    config['sub'] = {'b': 3}
    assert config['sub']['a'] == 100
    with pytest.raises(AttributeError):
        config['sub'].defaults = {'a': 200}
    assert config['sub']['a'] == 100

def test_Config_err_disabled_interpolation():
    config = Config(interpolation=False)
    config['x'] = 10
    config['sub'] = {'sub': {}}
    with pytest.raises(ValueError) as exc_info:
        config['y'] = ROOT['x'] + 1
    assert str(exc_info.value) == "cannot set y=ROOT['x'] + 1: interpolation is not enabled"
    with pytest.raises(ValueError) as exc_info:
        config['sub']['sub']['y'] = ROOT['x'] + 1
    assert str(exc_info.value) == "cannot set y=ROOT['x'] + 1: interpolation is not enabled"
    config.interpolation = True
    config['sub']['sub']['y'] = ROOT['x'] + 1
    assert config['sub']['sub']['y'] == 11
    config.interpolation = False
    with pytest.raises(ValueError) as exc_info:
        c = config['sub']['sub']['y']
    assert str(exc_info.value) == "cannot evaluate ROOT['x'] + 1: interpolation is not enabled"

def test_Config_change_defaults():
    config1 = Config(defaults=True)
    defaults1 = config1.defaults
    config1.set_defaults(s={'a': 1, 'b': 2})
    config2 = Config(defaults=True)
    defaults2 = config2.defaults
    config2.set_defaults(s={'a': 10, 'c': 20})

    assert config1['s']['a'] == 1
    assert config2['s']['a'] == 10

    config1.defaults = None

    config2.defaults = defaults1

    config1.defaults = defaults2

    assert config1.has_section('s')
    assert config1['s']['a'] == 10
    assert config2['s']['a'] == 1
