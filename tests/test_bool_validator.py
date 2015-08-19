# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from zirkon.validator.error import InvalidTypeError, \
                                   MissingRequiredOptionError
from zirkon.validator.bool_validators import Bool

def test_basic():
    bv = Bool()
    v = bv.validate(name='alpha', defined=True, value=True)
    assert v == True
    v = bv.validate(name='alpha', defined=True, value=False)
    assert v == False
    v = bv.validate(name='alpha', defined=True, value=0)
    assert v == False
    v = bv.validate(name='alpha', defined=True, value=12)
    assert v == True
    with pytest.raises(InvalidTypeError):
       v = bv.validate(name='alpha', defined=True, value=1.0)
    with pytest.raises(InvalidTypeError):
       v = bv.validate(name='alpha', defined=True, value='True')
    with pytest.raises(MissingRequiredOptionError):
        v = bv.validate(name='alpha', defined=False, value=None)

def test_default():
    bv = Bool(default=True)
    v = bv.validate(name='alpha', defined=True, value=False)
    assert v == False
    v = bv.validate(name='alpha', defined=False, value=None)
    assert v == True

def test_bad_default_type():
    with pytest.raises(InvalidTypeError):
        bv = Bool(default=2.9)


