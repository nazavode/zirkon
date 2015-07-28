# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from config import validator
from config.validator.error import TypeValidationError
from config.validator.validator_validator import ValidatorValidator

@pytest.fixture
def validator_validator():
    return validator.Validator.get_plugin('Validator')()

def test_validator_validator_from_string_ok(validator_validator):
    validator_string = "IntTuple(min_len=4, item_max=3, default=(0, 2, 1, 0, 2))"
    validator_instance = validator_validator.validate(key='<key>', value=validator_string, defined=True)
    assert isinstance(validator_instance, validator.IntTupleValidator)

def test_validator_validator_from_string_err0(validator_validator):
    validator_string = "IntTuple(min_len=4, item_max=3, default=(0, 2, 1, 0, 2)"
    with pytest.raises(TypeValidationError) as exc_info:
        validator_instance = validator_validator.validate(key='<key>', value=validator_string, defined=True)
    assert str(exc_info.value) == """<key>='IntTuple(min_len=4, item_max=3, default=(0, 2, 1, 0, 2)': cannot create a validator from string 'IntTuple(min_len=4, item_max=3, default=(0, 2, 1, 0, 2)': SyntaxError: unexpected EOF while parsing (<string>, line 1)"""

def test_validator_validator_from_string_err1(validator_validator):
    validator_string = "list((2, 3, 4))"
    with pytest.raises(TypeValidationError) as exc_info:
        validator_instance = validator_validator.validate(key='<key>', value=validator_string, defined=True)
    assert str(exc_info.value) == """<key>=[2, 3, 4]: invalid type list - expected type is Validator"""
