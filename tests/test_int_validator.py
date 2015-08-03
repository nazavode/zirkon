# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from daikon.validator.error import MinValidationError, \
                                   MaxValidationError, \
                                   TypeValidationError, \
                                   UndefinedKeyValidationError
from daikon.validator.int_validators import Int

def test_basic():
    iv = Int()
    v = iv.validate(key='alpha', defined=True, value=2)
    assert v == 2
    v = iv.validate(key='alpha', defined=True, value=-2000)
    assert v == -2000
    with pytest.raises(TypeValidationError):
        v = iv.validate(key='alpha', defined=True, value=2.0)
    with pytest.raises(UndefinedKeyValidationError):
        v = iv.validate(key='alpha', defined=False, value=None)

def test_default():
    iv = Int(default=10)
    v = iv.validate(key='alpha', defined=True, value=2)
    assert v == 2
    v = iv.validate(key='alpha', defined=False, value=None)
    assert v == 10
    v = iv.validate(key='alpha', defined=True, value=3)
    assert v == 3

def test_bad_default_type():
    with pytest.raises(TypeValidationError):
        iv = Int(default='ten')

def test_bad_default_min():
    with pytest.raises(TypeValidationError):
        iv = Int(min=4.5)

def test_bad_default_max():
    with pytest.raises(TypeValidationError):
        iv = Int(max=4.5)

def test_default_min():
    iv = Int(default=10, min=3)
    with pytest.raises(MinValidationError):
        v = iv.validate(key='alpha', defined=True, value=2)
    v = iv.validate(key='alpha', defined=True, value=3)
    assert v == 3
    v = iv.validate(key='alpha', defined=False, value=None)
    assert v == 10

def test_bad_min_type():
    with pytest.raises(MinValidationError):
        iv = Int(default=2, min=3)

def test_bad_max_type():
    with pytest.raises(MaxValidationError):
        iv = Int(default=101, max=100)

def test_default_max():
    iv = Int(default=10, min=3, max=100)
    with pytest.raises(MinValidationError):
        v = iv.validate(key='alpha', defined=True, value=2)
    with pytest.raises(MaxValidationError):
        v = iv.validate(key='alpha', defined=True, value=101)
    v = iv.validate(key='alpha', defined=True, value=3)
    assert v == 3
    v = iv.validate(key='alpha', defined=True, value=100)
    assert v == 100
    v = iv.validate(key='alpha', defined=False, value=None)
    assert v == 10

