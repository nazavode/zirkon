# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from daikon.validator.error import MinLengthError, \
                                   MaxLengthError, \
                                   InvalidTypeError, \
                                   MissingRequiredOptionError
from daikon.validator.str_validators import Str

def test_basic():
    sv = Str()
    v = sv.validate(name='alpha', defined=True, value='abc')
    assert v == 'abc'
    v = sv.validate(name='alpha', defined=True, value=' fg ')
    assert v == ' fg '
    v = sv.validate(name='alpha', defined=True, value='2')
    assert v == '2'
    with pytest.raises(InvalidTypeError):
        v = sv.validate(name='alpha', defined=True, value=2.0)
    with pytest.raises(MissingRequiredOptionError):
        v = sv.validate(name='alpha', defined=False, value=None)

def test_default():
    sv = Str(default='x.dat')
    v = sv.validate(name='alpha', defined=True, value='a.dat')
    assert v == 'a.dat'
    v = sv.validate(name='alpha', defined=False, value=None)
    assert v == 'x.dat'

def test_bad_default_type():
    with pytest.raises(InvalidTypeError):
        sv = Str(default=2)

def test_default_min_len():
    iv = Str(default="abcd", min_len=3)
    with pytest.raises(MinLengthError):
        v = iv.validate(name='alpha', defined=True, value="x")
    v = iv.validate(name='alpha', defined=True, value="xxx")
    assert v == "xxx"
    v = iv.validate(name='alpha', defined=False, value=None)
    assert v == "abcd"

def test_bad_default_min_len():
    with pytest.raises(MinLengthError):
        iv = Str(default="ab", min_len=3)

def test_bad_default_max_len():
    with pytest.raises(MaxLengthError):
        iv = Str(default="abcd", max_len=3)

def test_default_max_len():
    iv = Str(default="abcd", min_len=3, max_len=10)
    with pytest.raises(MinLengthError):
        v = iv.validate(name='alpha', defined=True, value="ab")
    with pytest.raises(MaxLengthError):
        v = iv.validate(name='alpha', defined=True, value="abcdefghijk")
    v = iv.validate(name='alpha', defined=True, value="xxx")
    assert v == "xxx"
    v = iv.validate(name='alpha', defined=True, value="abcdefghij")
    assert v == "abcdefghij"
    v = iv.validate(name='alpha', defined=False, value=None)
    assert v == "abcd"

def test_invalid_min_max():
    with pytest.raises(TypeError):
        Str(default="abcd", min_len=3, min=3)
    with pytest.raises(TypeError):
        Str(default="abcd", min_len=3, max=10)
