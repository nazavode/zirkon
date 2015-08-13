# -*- coding: utf-8 -*-

import pytest

from daikon.validator.key_value import KeyValue


def test_key_value_is_defined():
    key_value = KeyValue(key='alpha', value=8.3, defined=True)
    assert key_value.key == 'alpha'
    assert key_value.value == 8.3
    assert key_value.defined

def test_key_value_is_defined_True():
    key_value = KeyValue(key='alpha', value=8.3, defined=True)
    assert key_value.is_defined()

def test_key_value_is_defined_False():
    key_value = KeyValue(key='alpha', value=8.3, defined=False)
    assert not key_value.is_defined()

def test_key_value_is_defined_default():
    key_value = KeyValue(key='alpha', value=8.3)
    assert key_value.defined
    assert key_value.is_defined()
 
def test_key_value_copy():
    key_value = KeyValue(key='alpha', value=8.3, defined=True)
    key_value_copy = key_value.copy()
    assert key_value.key == 'alpha'
    assert key_value.value == 8.3
    assert key_value.defined

