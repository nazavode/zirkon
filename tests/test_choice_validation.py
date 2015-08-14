# -*- coding: utf-8 -*-

import collections
import inspect
import os

import pytest

from daikon.validator.error import InvalidChoiceError, \
                                   InvalidTypeError
from daikon.validator.int_validators import IntChoice
from daikon.validator.float_validators import FloatChoice
from daikon.validator.str_validators import StrChoice
from daikon.validator.bool_validators import BoolChoice

scenario = collections.OrderedDict()

Parameters = collections.namedtuple('Parameters', ('validator_class', 'choices', 'invalid_value', 'invalid_option'))

scenario['int'] = Parameters(
    validator_class=IntChoice,
    choices=(3, 4, 7),
    invalid_value=2,
    invalid_option="invalid_int_option")

scenario['float'] = Parameters(
    validator_class=FloatChoice,
    choices=(3.1, 4.2, 7.3),
    invalid_value=3.2,
    invalid_option="invalid_float_option")

scenario['str'] = Parameters(
    validator_class=StrChoice,
    choices=("alpha", "beta", "gamma"),
    invalid_value="delta",
    invalid_option=333)

scenario['bool'] = Parameters(
    validator_class=BoolChoice,
    choices=(True, ),
    invalid_value=False,
    invalid_option="invalid_bool_option")

@pytest.fixture(params=tuple(scenario.values()), ids=tuple(scenario.keys()))
def parameters(request):
    return request.param

def test_missing_required_argument(parameters):
    with pytest.raises(TypeError):
        iv = parameters.validator_class()

def test_basic(parameters):
    iv = parameters.validator_class(choices=parameters.choices)
    for value in parameters.choices:
        v = iv.validate(name='alpha', defined=True, value=value)
        assert v == value
    with pytest.raises(InvalidChoiceError):
        v = iv.validate(name='alpha', defined=True, value=parameters.invalid_value)

def test_bad_option_value(parameters):
    invalid_choices = parameters.choices + (parameters.invalid_option, )
    with pytest.raises(InvalidTypeError):
        iv = parameters.validator_class(choices=invalid_choices)
