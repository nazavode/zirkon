# -*- coding: utf-8 -*-

import collections
import inspect
import os

import pytest

from zirkon import validator

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
scenario['IntChoice'] = Parameters(
    validator_name='IntChoice',
    validator_class=validator.IntChoice,
    validator_options={'choices': (2, 3)})

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
scenario['FloatChoice'] = Parameters(
    validator_name='FloatChoice',
    validator_class=validator.FloatChoice,
    validator_options={'choices': (2.1, 3.1)})

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
scenario['StrChoice'] = Parameters(
    validator_name='StrChoice',
    validator_class=validator.StrChoice,
    validator_options={'choices': ('a', 'bb')})

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
scenario['BoolChoice'] = Parameters(
    validator_name='BoolChoice',
    validator_class=validator.BoolChoice,
    validator_options={'choices': (True, False)})

scenario['ValidatorInstance'] = Parameters(
    validator_name='ValidatorInstance',
    validator_class=validator.ValidatorInstance,
    validator_options={})

@pytest.fixture(params=tuple(scenario.values()), ids=tuple(scenario.keys()))
def parameters(request):
    return request.param

@pytest.fixture
def validator_validator():
    return validator.Validator.get_class('ValidatorInstance')()


def test_validator(validator_validator, parameters):
    validator_class = validator.Validator.get_class(parameters.validator_name)
    assert validator_class is parameters.validator_class
    validator_instance = validator_class(**parameters.validator_options)
    assert validator_instance is validator_validator.validate(name='<key>', value=validator_instance, defined=True)
