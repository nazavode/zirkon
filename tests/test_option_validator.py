# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from daikon.validator.error import InvalidOptionValidationError, \
                                   TypeValidationError
from daikon.validator.int_validators import IntOption
from daikon.validator.float_validators import FloatOption
from daikon.validator.str_validators import StrOption
from daikon.validator.bool_validators import BoolOption

from common.test_scenarios import pytest_generate_tests
    
class TestOptionWithScenarios(object):
    scenario_int = ('int',
        dict(validator_class=IntOption,
             values=(3, 4, 7),
             invalid_value=2,
             invalid_option="invalid_int_option"))
    scenario_float = ('float',
        dict(validator_class=FloatOption,
             values=(3.1, 4.2, 7.3),
             invalid_value=3.2,
             invalid_option="invalid_float_option"))
    scenario_str = ('str',
        dict(validator_class=StrOption,
             values=("alpha", "beta", "gamma"),
             invalid_value="delta",
             invalid_option=333))
    scenario_bool = ('bool',
        dict(validator_class=BoolOption,
             values=(True, ),
             invalid_value=False,
             invalid_option="invalid_bool_option"))
    scenarios = (scenario_int, scenario_float, scenario_str, scenario_bool)

    def test_missing_required_argument(self, validator_class, values, invalid_value, invalid_option):
        with pytest.raises(TypeError):
            iv = validator_class()

    def test_basic(self, validator_class, values, invalid_value, invalid_option):
        iv = validator_class(values=values)
        for value in values:
            v = iv.validate(key='alpha', defined=True, value=value)
            assert v == value
        with pytest.raises(InvalidOptionValidationError):
            v = iv.validate(key='alpha', defined=True, value=invalid_value)

    def test_bad_option_value(self, validator_class, values, invalid_value, invalid_option):
        invalid_values = values + (invalid_option, )
        with pytest.raises(TypeValidationError):
            iv = validator_class(values=invalid_values)
