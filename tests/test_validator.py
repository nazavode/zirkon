# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from daikon import validator
from daikon.validator.error import TypeValidationError
from daikon.validator.validator import Validator

@pytest.fixture
def validator_validator():
    return validator.ValidatorBase.get_plugin('Validator')()

def test_validator_from_string_ok(validator_validator):
    validator_string = "IntTuple(min_len=4, item_max=3, default=(0, 2, 1, 0, 2))"
    validator_instance = validator_validator.validate(key='<key>', value=validator_string, defined=True)
    assert isinstance(validator_instance, validator.IntTuple)

#def test_validator_from_string_err_no_load(validator_validator):
#    validator_string = "IntTuple(min_len=4, item_max=3, default=(0, 2, 1, 0, 2))"
#    with pytest.raises(TypeValidationError) as exc_info:
#        validator_instance = validator_validator.validate(key='<key>', value=validator_string, defined=True)
#    assert str(exc_info.value) == """<key>='IntTuple(min_len=4, item_max=3, default=(0, 2, 1, 0, 2))': invalid type str - expected type is ValidatorBase"""

def test_validator_from_string_err0(validator_validator):
    validator_string = "IntTuple(min_len=4, item_max=3, default=(0, 2, 1, 0, 2)"
    with pytest.raises(TypeValidationError) as exc_info:
        validator_instance = validator_validator.validate(key='<key>', value=validator_string, defined=True)
    assert str(exc_info.value) == """<key>='IntTuple(min_len=4, item_max=3, default=(0, 2, 1, 0, 2)': cannot create a validator from string 'IntTuple(min_len=4, item_max=3, default=(0, 2, 1, 0, 2)': SyntaxError: unexpected EOF while parsing (<string>, line 1)"""

def test_validator_from_string_err1(validator_validator):
    validator_string = "list((2, 3, 4))"
    with pytest.raises(TypeValidationError) as exc_info:
        validator_instance = validator_validator.validate(key='<key>', value=validator_string, defined=True)
    assert str(exc_info.value) == """<key>=[2, 3, 4]: invalid type list - expected type is ValidatorBase"""

def test_validator_to_string(validator_validator):
    validator_string = "IntTuple(min_len=4, item_max=3, default=(0, 2, 1, 0, 2))"
    validator_instance = validator_validator.validate(key='<key>', value=validator_string, defined=True)
    assert isinstance(validator_instance, validator.IntTuple)
    validator_instance_string = validator_instance.repr()
    validator_instance2 = validator_validator.validate(key='<key>', value=validator_instance_string, defined=True)
    assert isinstance(validator_instance2, validator.IntTuple)
    assert validator_instance == validator_instance2

