# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from config.utils import loader


def test_load_module_mypack():
    obj = loader.load_module('mypack')
    assert inspect.ismodule(obj)
    assert obj.__name__ == 'mypack'


def test_load_mypack():
    obj = loader.load('mypack')
    assert inspect.ismodule(obj)
    assert obj.__name__ == 'mypack'


def test_load_mypack_one():
    obj = loader.load('mypack:one')
    assert inspect.isfunction(obj)
    assert obj() == 1


def test_load_mypack_two():
    with pytest.raises(loader.LoaderError) as exc_info:
        obj = loader.load('mypack:two')
    assert str(exc_info.value) == "cannot load object two from mypack"


def test_load_module_mypack2():
    with pytest.raises(loader.LoaderError) as exc_info:
        obj = loader.load_module('mypack2')
    assert str(exc_info.value) == "cannot load top-level package mypack2"


def test_load_module_mypack2_mymod():
    with pytest.raises(loader.LoaderError) as exc_info:
        obj = loader.load_module('mypack2.mymod')
    assert str(exc_info.value) == "cannot load top-level package mypack2"


def test_load_module_mypack_mymod2_mysubmod():
    with pytest.raises(loader.LoaderError) as exc_info:
        obj = loader.load_module('mypack.mymod2.mysubmod')
    assert str(exc_info.value) == "cannot load package mymod2 from mypack"


def test_load_module_mypack_mymod2():
    with pytest.raises(loader.LoaderError) as exc_info:
        obj = loader.load_module('mypack.mymod2')
    assert str(exc_info.value) == "cannot load module mymod2 from mypack"


def test_load_mypack_mymod2():
    with pytest.raises(loader.LoaderError) as exc_info:
        obj = loader.load('mypack.mymod2')
    assert str(exc_info.value) == "cannot load module mymod2 from mypack"


def test_load_module_mypack_mymod():
    obj = loader.load_module('mypack.mymod')
    assert inspect.ismodule(obj)
    assert obj.__name__ == 'mypack.mymod'


def test_load_mypack_mymod():
    obj = loader.load('mypack.mymod')
    assert inspect.ismodule(obj)
    assert obj.__name__ == 'mypack.mymod'


def test_load_mypack_mysubpack():
    obj = loader.load('mypack.mysubpack')
    assert inspect.ismodule(obj)
    assert obj.__name__ == 'mypack.mysubpack'


def test_load_mypack_mysubpack_four():
    obj = loader.load('mypack.mysubpack:four')
    assert inspect.isfunction(obj)
    assert obj() == 4


def test_load_mypack_mysubpack_mymod():
    obj = loader.load('mypack.mysubpack.mymod')
    assert inspect.ismodule(obj)
    assert obj.__name__ == 'mypack.mysubpack.mymod'


def test_load_mypack_mysubpack_twentyfive():
    obj = loader.load('mypack.mysubpack.mymod:twentyfive')
    assert inspect.isfunction(obj)
    assert obj() == 25


def test_load_mypack_mymod_five():
    obj = loader.load('mypack.mymod:five')
    assert inspect.isfunction(obj)
    assert obj() == 5


def test_load_abs_mypack_mymod_five():
    obj = loader.load(os.path.join(os.getcwd(), 'mypack.mymod:five'))
    assert inspect.isfunction(obj)
    assert obj() == 5


def test_load_path_mypack_mymod_five():
    obj = loader.load(path=[os.getcwd()], name='mypack.mymod:five')
    assert inspect.isfunction(obj)
    assert obj() == 5


def test_load_path_mypack_mymod_sixteen():
    obj = loader.load(path=[os.getcwd()], name='mypack.mymod:sixteen')
    assert inspect.isfunction(obj)
    assert obj() == 16
