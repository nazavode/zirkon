# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from daikon import validator
from daikon.validator.validator_validator import ValidatorValidator

from common.test_scenarios import pytest_generate_tests

@pytest.fixture
def validator_validator():
    return validator.Validator.get_plugin('Validator')()

class TestWithScenarios(object):
    scenario_Int = ('Int',
        dict(validator_name='Int',
             validator_class=validator.IntValidator,
             validator_options={'default': 2}))
    scenario_IntList = ('IntList',
        dict(validator_name='IntList',
             validator_class=validator.IntListValidator,
             validator_options={'item_max': 20, 'min_len': 3, 'max_len': 100, 'default': [4, 4, 4]}))
    scenario_IntTuple = ('IntTuple',
        dict(validator_name='IntTuple',
             validator_class=validator.IntTupleValidator,
             validator_options={'item_min': 2, 'max_len': 4}))
    scenario_IntOption = ('IntOption',
        dict(validator_name='IntOption',
             validator_class=validator.IntOptionValidator,
             validator_options={'values': (2, 3)}))

    scenario_Float = ('Float',
        dict(validator_name='Float',
             validator_class=validator.FloatValidator,
             validator_options={'default': 3.5}))
    scenario_FloatList = ('FloatList',
        dict(validator_name='FloatList',
             validator_class=validator.FloatListValidator,
             validator_options={'default': [3.4, 4.3], 'min_len': 2, 'item_max': 10.0}))
    scenario_FloatTuple = ('FloatTuple',
        dict(validator_name='FloatTuple',
             validator_class=validator.FloatTupleValidator,
             validator_options={'min_len': 2}))
    scenario_FloatOption = ('FloatOption',
        dict(validator_name='FloatOption',
             validator_class=validator.FloatOptionValidator,
             validator_options={'values': (2.1, 3.1)}))

    scenario_Str = ('Str',
        dict(validator_name='Str',
             validator_class=validator.StrValidator,
             validator_options={'default': 'abcd'}))
    scenario_StrList = ('StrList',
        dict(validator_name='StrList',
             validator_class=validator.StrListValidator,
             validator_options={'default': ["a", "c", "b"]}))
    scenario_StrTuple = ('StrTuple',
        dict(validator_name='StrTuple',
             validator_class=validator.StrTupleValidator,
             validator_options={'min_len': 4, 'max_len': 9}))
    scenario_StrOption = ('StrOption',
        dict(validator_name='StrOption',
             validator_class=validator.StrOptionValidator,
             validator_options={'values': ('a', 'bb')}))

    scenario_Bool = ('Bool',
        dict(validator_name='Bool',
             validator_class=validator.BoolValidator,
             validator_options={'default': False}))
    scenario_BoolList = ('BoolList',
        dict(validator_name='BoolList',
             validator_class=validator.BoolListValidator,
             validator_options={'min_len': 10}))
    scenario_BoolTuple = ('BoolTuple',
        dict(validator_name='BoolTuple',
             validator_class=validator.BoolTupleValidator,
             validator_options={'max_len': 5}))
    scenario_BoolOption = ('BoolOption',
        dict(validator_name='BoolOption',
             validator_class=validator.BoolOptionValidator,
             validator_options={'values': (True, False)}))

    scenario_Validator = ('Validator',
        dict(validator_name='Validator',
             validator_class=ValidatorValidator,
             validator_options={}))

    scenarios = (
        scenario_Int, scenario_IntList, scenario_IntTuple, scenario_IntOption,
        scenario_Float, scenario_FloatList, scenario_FloatTuple, scenario_FloatOption,
        scenario_Str, scenario_StrList, scenario_StrTuple, scenario_StrOption,
        scenario_Bool, scenario_BoolList, scenario_BoolTuple, scenario_BoolOption,
        scenario_Validator,
    )

    def test_validator(self, validator_validator, validator_name, validator_class, validator_options):
        validator_plugin = validator.Validator.get_plugin(validator_name)
        assert validator_plugin is validator_class
        validator_instance = validator_plugin(**validator_options)
        assert validator_instance is validator_validator.validate(key='<key>', value=validator_instance, defined=True)
        
        validator_repr = validator_instance.validator_repr()
        validator_instance2 = validator_validator.validate('<key>', value=validator_repr, defined=True)
        assert validator_instance == validator_instance2

        validator_instance3 = validator.Validator.validator_unrepr(validator_instance2.validator_repr())
        assert validator_instance == validator_instance3
