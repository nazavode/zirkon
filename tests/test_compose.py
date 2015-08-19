# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from zirkon.toolbox.compose import ArgumentStore, Composer

class Alpha(object):
    def __init__(self, x, y=10):
        self.x = x
        self.y = y

    def __repr__(self):
        return "{}(x={!r}, y={!r})".format(self.__class__.__name__, self.x, self.y)

class Beta(Alpha):
    def __init__(self, xy):
        super().__init__(xy[0], xy[1])
        self.x, self.y = xy

    @classmethod
    def build(cls, xx, yy):
        return cls((xx, yy))

    def __repr__(self):
        return "{}(x={!r}, y={!r})".format(self.__class__.__name__, self.x, self.y)


def gamma(a, b, c):
    return [a, b, c]

def fab(a, b):
    return [a, b]

def fbc(b, c):
    return [b, c]

def _check_objects(objects):
    assert isinstance(objects[0], Alpha)
    assert objects[0].x == 11
    assert objects[0].y == 10
    assert isinstance(objects[1], Beta)
    assert objects[1].x == 13
    assert objects[1].y == 14
    assert isinstance(objects[2], Beta)
    assert objects[2].x == 23
    assert objects[2].y == 24
    assert isinstance(objects[3], list)
    assert objects[3] == [100, 200, 300]

def _check_actual_arguments(actual_arguments):
    kwlist = list(actual_arguments.items())
    assert kwlist[0] == ('x', 11)
    assert kwlist[1] == ('xy', (13, 14))
    assert kwlist[2] == ('xx', 23)
    assert kwlist[3] == ('yy', 24)
    assert kwlist[4] == ('a', 100)
    assert kwlist[5] == ('b', 200)
    assert kwlist[6] == ('c', 300)

def _check_actual_arguments_y(actual_arguments):
    kwlist = list(actual_arguments.items())
    assert kwlist[0] == ('x', 11)
    assert kwlist[1] == ('y', 10)
    assert kwlist[2] == ('xy', (13, 14))
    assert kwlist[3] == ('xx', 23)
    assert kwlist[4] == ('yy', 24)
    assert kwlist[5] == ('a', 100)
    assert kwlist[6] == ('b', 200)
    assert kwlist[7] == ('c', 300)

@pytest.fixture()
def composer():
    return Composer(Alpha, Beta, Beta.build, gamma)

def fsub(item_min, item_max, item_type):
    return [item_type, item_min, item_max]

@pytest.fixture()
def subcomposer():
    return Composer(fsub)

def _check_sub_objects(objects):
    assert isinstance(objects[0], list)
    assert objects[0][0] == 'int'
    assert objects[0][1] == 5
    assert objects[0][2] == 10

def _check_actual_sub_arguments(actual_arguments):
    kwlist = list(actual_arguments.items())
    assert kwlist[0] == ('item_min', 5)
    assert kwlist[1] == ('item_max', 10)
    assert kwlist[2] == ('item_type', 'int')

def test_Composer_simple_ok(composer):
    actual_arguments, objects = composer(a=100, x=11, c=300, xy=(13, 14), yy=24, b=200, xx=23)
    _check_actual_arguments(actual_arguments)
    _check_objects(objects)

def test_Composer_simple_missing(composer):
    with pytest.raises(TypeError) as exc_info:
        actual_arguments, objects = composer(x=11, xy=(13, 14), yy=24, a=100, b=200, c=300, y=10)
    assert str(exc_info.value) == "build: missing required argument xx"

def test_Composer_simple_unexpected(composer):
    with pytest.raises(TypeError) as exc_info:
        actual_arguments, objects = composer(x=11, xy=(13, 14), xx=23, zz=45, yy=24, a=100, b=200, c=300)
    assert str(exc_info.value) == "unexpected arguments: zz=45"

def test_Composer_partial(composer):
    arguments = dict(x=11, xy=(13, 14), xx=23, zz=45, yy=24, a=100, b=200, c=300)
    argument_store = ArgumentStore(arguments)
    actual_arguments, objects = composer.partial(argument_store)
    _check_actual_arguments(actual_arguments)
    _check_objects(objects)
    with pytest.raises(TypeError) as exc_info:
        composer.verify_argument_store(argument_store)
    assert str(exc_info.value) == "unexpected arguments: zz=45"

def test_Composer_partial(composer, subcomposer):
    arguments = dict(x=11, xy=(13, 14), xx=23, item_max=10, item_min=5, zz=45, item_type='int', yy=24, a=100, b=200, c=300)
    argument_store = ArgumentStore(arguments)
    actual_arguments, objects = composer.partial(argument_store)
    _check_actual_arguments(actual_arguments)
    _check_objects(objects)
    sub_actual_arguments, sub_objects = subcomposer.partial(argument_store)
    _check_actual_sub_arguments(sub_actual_arguments)
    _check_sub_objects(sub_objects)
    with pytest.raises(TypeError) as exc_info:
        composer.verify_argument_store(argument_store)
    assert str(exc_info.value) == "unexpected arguments: zz=45"

def test_Composer_sub(composer):
    arguments = dict(x=11, xy=(13, 14), xx=23, yy=24, a=100, b=200, c=300, sub_a=111, sub_b=222, sub_c=333)
    argument_store = ArgumentStore(arguments)
    actual_arguments, objects = composer.partial(argument_store)
    _check_objects(objects)
    sub_composer = Composer(fab, fbc)
    sub_actual_arguments, sub_objects = sub_composer.partial(argument_store, prefix='sub_')
    assert sub_objects[0] == [111, 222]
    assert sub_objects[1] == [222, 333]
    composer.verify_argument_store(argument_store)

def test_Composer_sub_missing(composer):
    arguments = dict(x=11, xy=(13, 14), xx=23, yy=24, a=100, b=200, c=300, sub_a=111, sub_c=333)
    argument_store = ArgumentStore(arguments)
    actual_arguments, objects = composer.partial(argument_store)
    _check_objects(objects)
    sub_composer = Composer(fab, fbc)
    with pytest.raises(TypeError) as exc_info:
        sub_actual_arguments, sub_objects = sub_composer.partial(argument_store, prefix='sub_')
    assert str(exc_info.value) == "fab: missing required argument b"

def test_Composer_sub_unexpected(composer):
    arguments = dict(x=11, xy=(13, 14), xx=23, yy=24, zz=45, a=100, b=200, c=300, sub_a=111, sub_b=222, sub_c=333, sub_d=444)
    argument_store = ArgumentStore(arguments)
    actual_arguments, objects = composer.partial(argument_store)
    _check_objects(objects)
    sub_composer = Composer(fab, fbc)
    sub_actual_arguments, sub_objects = sub_composer.partial(argument_store, prefix='sub_')
    assert sub_objects[0] == [111, 222]
    assert sub_objects[1] == [222, 333]
    with pytest.raises(TypeError) as exc_info:
        composer.verify_argument_store(argument_store)
    assert str(exc_info.value) == "unexpected arguments: sub_d=444, zz=45"

def test_ArgumentStore_split_merge():
    d = dict(min_len=1, max_len=5, default=[5, 6, 7], item_min=3, item_max=18)
    argument_store = ArgumentStore(d)
    sub_argument_store = argument_store.split(prefix='item_')
    l = list(sub_argument_store.items())
    l.sort(key=lambda x: x[0])
    assert l[0][0] == 'max'
    assert l[0][1] == 18
    assert l[1][0] == 'min'
    assert l[1][1] == 3
    assert sub_argument_store.get('min') == 3
    assert argument_store.get('max_len') == 5
    argument_store.merge(sub_argument_store, prefix='item_')
    assert argument_store.get('default') == [5, 6, 7]
    assert argument_store.get_used('item_min')
    assert not argument_store.get_used('item_max')
    assert not argument_store.get_used('min_len')
    assert argument_store.get_used('max_len')
    assert argument_store.get_used('default')
