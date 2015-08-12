# -*- coding: utf-8 -*-

import collections
import inspect
import os

import pytest

from daikon.validator.error import OptionValidationError, \
                                   InvalidTypeError
from daikon.validator.int_validators import IntOption
from daikon.validator.float_validators import FloatOption
from daikon.validator.str_validators import StrOption
from daikon.validator.bool_validators import BoolOption

scenario = collections.OrderedDict()

Parameters = collections.namedtuple('Parameters', ('validator_class', 'values', 'invalid_value', 'invalid_option'))

scenario['int'] = Parameters(
    validator_class=IntOption,
    values=(3, 4, 7),
    invalid_value=2,
    invalid_option="invalid_int_option")

scenario['float'] = Parameters(
    validator_class=FloatOption,
    values=(3.1, 4.2, 7.3),
    invalid_value=3.2,
    invalid_option="invalid_float_option")

scenario['str'] = Parameters(
    validator_class=StrOption,
    values=("alpha", "beta", "gamma"),
    invalid_value="delta",
    invalid_option=333)

scenario['bool'] = Parameters(
    validator_class=BoolOption,
    values=(True, ),
    invalid_value=False,
    invalid_option="invalid_bool_option")

@pytest.fixture(params=tuple(scenario.values()), ids=tuple(scenario.keys()))
def parameters(request):
    return request.param

def test_missing_required_argument(parameters):
    with pytest.raises(TypeError):
        iv = parameters.validator_class()

def test_basic(parameters):
    iv = parameters.validator_class(values=parameters.values)
    for value in parameters.values:
        v = iv.validate(key='alpha', defined=True, value=value)
        assert v == value
    with pytest.raises(OptionValidationError):
        v = iv.validate(key='alpha', defined=True, value=parameters.invalid_value)

def test_bad_option_value(parameters):
    invalid_values = parameters.values + (parameters.invalid_option, )
    with pytest.raises(InvalidTypeError):
        iv = parameters.validator_class(values=invalid_values)
