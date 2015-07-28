# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from config.utils.singleton import Singleton


def test_singleton():
    class Alpha(metaclass=Singleton):
        pass
    a = Alpha()
    b = Alpha()
    assert a == b
    assert a is b

