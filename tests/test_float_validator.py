# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from zirkon.validator.error import MinValueError, \
                                   MaxValueError, \
                                   InvalidTypeError, \
                                   MissingRequiredOptionError
from zirkon.validator.float_validators import Float

def test_basic():
    fv = Float()
    v = fv.validate(name='alpha', defined=True, value=2.0)
    assert v == 2.0
    v = fv.validate(name='alpha', defined=True, value=-2000.234)
    assert v == -2000.234
    v = fv.validate(name='alpha', defined=True, value=2)
    assert isinstance(v, float)
    assert v == 2.0
    with pytest.raises(InvalidTypeError):
        v = fv.validate(name='alpha', defined=True, value='2.0')
    with pytest.raises(MissingRequiredOptionError):
        v = fv.validate(name='alpha', defined=False, value=None)

def test_default():
    fv = Float(default=10)
    v = fv.validate(name='alpha', defined=True, value=2.2)
    assert v == 2.2
    v = fv.validate(name='alpha', defined=False, value=None)
    assert v == 10.0
    assert isinstance(v, float)
    v = fv.validate(name='alpha', defined=True, value=3.2)
    assert v == 3.2

def test_bad_default_type():
    with pytest.raises(InvalidTypeError):
        fv = Float(default='ten')

def test_bad_min_type():
    with pytest.raises(InvalidTypeError):
        iv = Float(min="abc")

def test_bad_max_type():
    with pytest.raises(InvalidTypeError):
        iv = Float(max="abc")

def test_default_min():
    fv = Float(default=10.01, min=3.3)
    with pytest.raises(MinValueError):
        v = fv.validate(name='alpha', defined=True, value=3.2)
    v = fv.validate(name='alpha', defined=True, value=3.3)
    assert v == 3.3
    v = fv.validate(name='alpha', defined=True, value=3.4)
    assert v == 3.4
    v = fv.validate(name='alpha', defined=False, value=None)
    assert v == 10.01

def test_bad_default_min():
    with pytest.raises(MinValueError):
        fv = Float(default=2.9, min=3.0)

def test_bad_default_max():
    with pytest.raises(MaxValueError):
        fv = Float(default=3.1, max=3.0)

def test_default_max():
    fv = Float(default=10.01, min=3.2, max=100.1)
    with pytest.raises(MinValueError):
        v = fv.validate(name='alpha', defined=True, value=3.199)
    with pytest.raises(MaxValueError):
        v = fv.validate(name='alpha', defined=True, value=100.101)
    v = fv.validate(name='alpha', defined=True, value=3.2)
    assert v == 3.2
    v = fv.validate(name='alpha', defined=True, value=100.1)
    assert v == 100.1
    v = fv.validate(name='alpha', defined=False, value=None)
    assert v == 10.01

