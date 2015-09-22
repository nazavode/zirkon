# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from zirkon.toolbox.loader import load

def test_import_all():
    module_names = load("zirkon:__all__")
    for module_name in module_names:
        module = load("zirkon:{}".format(module_name))

@pytest.fixture(params=['Config', 'Schema', 'Validation', 'ConfigValidationError', 'ROOT', 'SECTION'])
def obj_name(request):
    return request.param

def test_import_obj(obj_name):
    load('zirkon:{}'.format(obj_name))
