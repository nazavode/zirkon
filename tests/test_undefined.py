# -*- coding: utf-8 -*-

import pytest

from daikon.toolbox.undefined import UNDEFINED


def test_undefined():
    a = UNDEFINED
    assert a is UNDEFINED
    b = type(UNDEFINED)()
    assert b is UNDEFINED

