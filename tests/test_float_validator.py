# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from daikon.validator.error import MinValidationError, \
                                   MaxValidationError, \
                                   TypeValidationError, \
                                   UndefinedKeyValidationError
from daikon.validator.float_validator import FloatValidator

def test_basic():
    fv = FloatValidator()
    v = fv.validate(key='alpha', defined=True, value=2.0)
    assert v == 2.0
    v = fv.validate(key='alpha', defined=True, value=-2000.234)
    assert v == -2000.234
    v = fv.validate(key='alpha', defined=True, value=2)
    assert isinstance(v, float)
    assert v == 2.0
    with pytest.raises(TypeValidationError):
        v = fv.validate(key='alpha', defined=True, value='2.0')
    with pytest.raises(UndefinedKeyValidationError):
        v = fv.validate(key='alpha', defined=False, value=None)

def test_default():
    fv = FloatValidator(default=10)
    v = fv.validate(key='alpha', defined=True, value=2.2)
    assert v == 2.2
    v = fv.validate(key='alpha', defined=False, value=None)
    assert v == 10.0
    assert isinstance(v, float)
    v = fv.validate(key='alpha', defined=True, value=3.2)
    assert v == 3.2

def test_bad_default_type():
    with pytest.raises(TypeValidationError):
        fv = FloatValidator(default='ten')

def test_default_min():
    fv = FloatValidator(default=10.01, min=3.3)
    with pytest.raises(MinValidationError):
        v = fv.validate(key='alpha', defined=True, value=3.2)
    v = fv.validate(key='alpha', defined=True, value=3.3)
    assert v == 3.3
    v = fv.validate(key='alpha', defined=True, value=3.4)
    assert v == 3.4
    v = fv.validate(key='alpha', defined=False, value=None)
    assert v == 10.01

def test_bad_default_min():
    with pytest.raises(MinValidationError):
        fv = FloatValidator(default=2.9, min=3.0)

def test_bad_default_max():
    with pytest.raises(MaxValidationError):
        fv = FloatValidator(default=3.1, max=3.0)

def test_default_max():
    fv = FloatValidator(default=10.01, min=3.2, max=100.1)
    with pytest.raises(MinValidationError):
        v = fv.validate(key='alpha', defined=True, value=3.199)
    with pytest.raises(MaxValidationError):
        v = fv.validate(key='alpha', defined=True, value=100.101)
    v = fv.validate(key='alpha', defined=True, value=3.2)
    assert v == 3.2
    v = fv.validate(key='alpha', defined=True, value=100.1)
    assert v == 100.1
    v = fv.validate(key='alpha', defined=False, value=None)
    assert v == 10.01

