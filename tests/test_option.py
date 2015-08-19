# -*- coding: utf-8 -*-

import pytest

from zirkon.validator.option import Option


def test_option_is_defined():
    option = Option(name='alpha', value=8.3, defined=True)
    assert option.name == 'alpha'
    assert option.value == 8.3
    assert option.defined

def test_option_is_defined_True():
    option = Option(name='alpha', value=8.3, defined=True)
    assert option.is_defined()

def test_option_is_defined_False():
    option = Option(name='alpha', value=8.3, defined=False)
    assert not option.is_defined()

def test_option_is_defined_default():
    option = Option(name='alpha', value=8.3)
    assert option.defined
    assert option.is_defined()
 
def test_option_copy():
    option = Option(name='alpha', value=8.3, defined=True)
    option_copy = option.copy()
    assert option.name == 'alpha'
    assert option.value == 8.3
    assert option.defined

