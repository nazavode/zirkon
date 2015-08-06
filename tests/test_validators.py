# -*- coding: utf-8 -*-

import collections
import inspect
import os

import pytest

from daikon import validator

scenario = collections.OrderedDict()

Parameters = collections.namedtuple('Parameters', ('validator_name', 'validator_class', 'validator_options'))

scenario['Int'] = Parameters(
    validator_name='Int',
    validator_class=validator.Int,
    validator_options={'default': 2})
scenario['IntList'] = Parameters(
    validator_name='IntList',
    validator_class=validator.IntList,
    validator_options={'item_max': 20, 'min_len': 3, 'max_len': 100, 'default': [4, 4, 4]})
scenario['IntTuple'] = Parameters(
    validator_name='IntTuple',
    validator_class=validator.IntTuple,
    validator_options={'item_min': 2, 'max_len': 4})
scenario['IntOption'] = Parameters(
    validator_name='IntOption',
    validator_class=validator.IntOption,
    validator_options={'values': (2, 3)})

scenario['Float'] = Parameters(
    validator_name='Float',
    validator_class=validator.Float,
    validator_options={'default': 3.5})
scenario['FloatList'] = Parameters(
    validator_name='FloatList',
    validator_class=validator.FloatList,
    validator_options={'default': [3.4, 4.3], 'min_len': 2, 'item_max': 10.0})
scenario['FloatTuple'] = Parameters(
    validator_name='FloatTuple',
    validator_class=validator.FloatTuple,
    validator_options={'min_len': 2})
scenario['FloatOption'] = Parameters(
    validator_name='FloatOption',
    validator_class=validator.FloatOption,
    validator_options={'values': (2.1, 3.1)})

scenario['Str'] = Parameters(
    validator_name='Str',
    validator_class=validator.Str,
    validator_options={'default': 'abcd'})
scenario['StrList'] = Parameters(
    validator_name='StrList',
    validator_class=validator.StrList,
    validator_options={'default': ["a", "c", "b"]})
scenario['StrTuple'] = Parameters(
    validator_name='StrTuple',
    validator_class=validator.StrTuple,
    validator_options={'min_len': 4, 'max_len': 9})
scenario['StrOption'] = Parameters(
    validator_name='StrOption',
    validator_class=validator.StrOption,
    validator_options={'values': ('a', 'bb')})

scenario['Bool'] = Parameters(
    validator_name='Bool',
    validator_class=validator.Bool,
    validator_options={'default': False})
scenario['BoolList'] = Parameters(
    validator_name='BoolList',
    validator_class=validator.BoolList,
    validator_options={'min_len': 10})
scenario['BoolTuple'] = Parameters(
    validator_name='BoolTuple',
    validator_class=validator.BoolTuple,
    validator_options={'max_len': 5})
scenario['BoolOption'] = Parameters(
    validator_name='BoolOption',
    validator_class=validator.BoolOption,
    validator_options={'values': (True, False)})

scenario['ValidatorInstance'] = Parameters(
    validator_name='ValidatorInstance',
    validator_class=validator.ValidatorInstance,
    validator_options={})

@pytest.fixture(params=tuple(scenario.values()), ids=tuple(scenario.keys()))
def parameters(request):
    return request.param

@pytest.fixture
def validator_validator():
    return validator.Validator.get_plugin('ValidatorInstance')()


def test_validator(validator_validator, parameters):
    validator_plugin = validator.Validator.get_plugin(parameters.validator_name)
    assert validator_plugin is parameters.validator_class
    validator_instance = validator_plugin(**parameters.validator_options)
    assert validator_instance is validator_validator.validate(key='<key>', value=validator_instance, defined=True)
    
#    validator_repr = validator_instance.repr()
#    validator_instance2 = validator_validator.validate('<key>', value=validator_repr, defined=True)
#    assert validator_instance == validator_instance2
#
#    validator_instance3 = validator.Validator.unrepr(validator_instance2.repr())
#    assert validator_instance == validator_instance3

#class TestWithScenarios(object):
#    scenario_Int = ('Int',
#        dict(validator_name='Int',
#             validator_class=validator.Int,
#             validator_options={'default': 2}))
#    scenario_IntList = ('IntList',
#        dict(validator_name='IntList',
#             validator_class=validator.IntList,
#             validator_options={'item_max': 20, 'min_len': 3, 'max_len': 100, 'default': [4, 4, 4]}))
#    scenario_IntTuple = ('IntTuple',
#        dict(validator_name='IntTuple',
#             validator_class=validator.IntTuple,
#             validator_options={'item_min': 2, 'max_len': 4}))
#    scenario_IntOption = ('IntOption',
#        dict(validator_name='IntOption',
#             validator_class=validator.IntOption,
#             validator_options={'values': (2, 3)}))
#
#    scenario_Float = ('Float',
#        dict(validator_name='Float',
#             validator_class=validator.Float,
#             validator_options={'default': 3.5}))
#    scenario_FloatList = ('FloatList',
#        dict(validator_name='FloatList',
#             validator_class=validator.FloatList,
#             validator_options={'default': [3.4, 4.3], 'min_len': 2, 'item_max': 10.0}))
#    scenario_FloatTuple = ('FloatTuple',
#        dict(validator_name='FloatTuple',
#             validator_class=validator.FloatTuple,
#             validator_options={'min_len': 2}))
#    scenario_FloatOption = ('FloatOption',
#        dict(validator_name='FloatOption',
#             validator_class=validator.FloatOption,
#             validator_options={'values': (2.1, 3.1)}))
#
#    scenario_Str = ('Str',
#        dict(validator_name='Str',
#             validator_class=validator.Str,
#             validator_options={'default': 'abcd'}))
#    scenario_StrList = ('StrList',
#        dict(validator_name='StrList',
#             validator_class=validator.StrList,
#             validator_options={'default': ["a", "c", "b"]}))
#    scenario_StrTuple = ('StrTuple',
#        dict(validator_name='StrTuple',
#             validator_class=validator.StrTuple,
#             validator_options={'min_len': 4, 'max_len': 9}))
#    scenario_StrOption = ('StrOption',
#        dict(validator_name='StrOption',
#             validator_class=validator.StrOption,
#             validator_options={'values': ('a', 'bb')}))
#
#    scenario_Bool = ('Bool',
#        dict(validator_name='Bool',
#             validator_class=validator.Bool,
#             validator_options={'default': False}))
#    scenario_BoolList = ('BoolList',
#        dict(validator_name='BoolList',
#             validator_class=validator.BoolList,
#             validator_options={'min_len': 10}))
#    scenario_BoolTuple = ('BoolTuple',
#        dict(validator_name='BoolTuple',
#             validator_class=validator.BoolTuple,
#             validator_options={'max_len': 5}))
#    scenario_BoolOption = ('BoolOption',
#        dict(validator_name='BoolOption',
#             validator_class=validator.BoolOption,
#             validator_options={'values': (True, False)}))
#
#    scenario_ValidatorInstance = ('ValidatorInstance',
#        dict(validator_name='ValidatorInstance',
#             validator_class=validator.ValidatorInstance,
#             validator_options={}))
#
#    scenarios = (
#        scenario_Int, scenario_IntList, scenario_IntTuple, scenario_IntOption,
#        scenario_Float, scenario_FloatList, scenario_FloatTuple, scenario_FloatOption,
#        scenario_Str, scenario_StrList, scenario_StrTuple, scenario_StrOption,
#        scenario_Bool, scenario_BoolList, scenario_BoolTuple, scenario_BoolOption,
#        scenario_ValidatorInstance,
#    )
#
#    def test_validator(self, validator_validator, validator_name, validator_class, validator_options):
#        validator_plugin = validator.Validator.get_plugin(validator_name)
#        assert validator_plugin is validator_class
#        validator_instance = validator_plugin(**validator_options)
#        assert validator_instance is validator_validator.validate(key='<key>', value=validator_instance, defined=True)
#        
#        validator_repr = validator_instance.repr()
#        validator_instance2 = validator_validator.validate('<key>', value=validator_repr, defined=True)
#        assert validator_instance == validator_instance2
#
#        validator_instance3 = validator.Validator.unrepr(validator_instance2.repr())
#        assert validator_instance == validator_instance3
