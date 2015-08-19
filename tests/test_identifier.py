# -*- coding: utf-8 -*-

import os

import pytest

from zirkon.toolbox.identifier import is_valid_identifier

_data = [
    ('', False),
    ('a', True),
    ('_', True),
    ('_9', True),
    ('9', False),
    ('9aaa', False),
    ('%', False),
    ('A', True),
    ('A_', True),
    ('Aadsfdsa_', True),
    ('Aads.fdsa_', False),
    (123, False),
]

@pytest.fixture(params=_data, ids=[p[0] for p in _data])
def param(request):
    return request.param

def test_is_valid_identifier(param):
    identifier, is_valid = param
    assert is_valid_identifier(identifier) == is_valid
