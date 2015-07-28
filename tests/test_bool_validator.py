# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from daikon.validator.error import TypeValidationError, \
                                   UndefinedKeyValidationError
from daikon.validator.bool_validator import BoolValidator

def test_basic():
    bv = BoolValidator()
    v = bv.validate(key='alpha', defined=True, value=True)
    assert v == True
    v = bv.validate(key='alpha', defined=True, value=False)
    assert v == False
    v = bv.validate(key='alpha', defined=True, value=0)
    assert v == False
    v = bv.validate(key='alpha', defined=True, value=12)
    assert v == True
    with pytest.raises(TypeValidationError):
       v = bv.validate(key='alpha', defined=True, value=1.0)
    with pytest.raises(TypeValidationError):
       v = bv.validate(key='alpha', defined=True, value='True')
    with pytest.raises(UndefinedKeyValidationError):
        v = bv.validate(key='alpha', defined=False, value=None)

def test_default():
    bv = BoolValidator(default=True)
    v = bv.validate(key='alpha', defined=True, value=False)
    assert v == False
    v = bv.validate(key='alpha', defined=False, value=None)
    assert v == True

def test_bad_default_type():
    with pytest.raises(TypeValidationError):
        bv = BoolValidator(default=2.9)


