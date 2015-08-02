# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from daikon.utils.compose import ArgumentStore, Composer

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

def test_Composer_simple_ok():
    composer = Composer(Alpha, Beta, Beta.build, gamma)
    objects = composer(x=11, xy=(13, 14), xx=23, yy=24, a=100, b=200, c=300)
    _check_objects(objects)

def test_Composer_simple_missing():
    composer = Composer(Alpha, Beta, Beta.build, gamma)
    with pytest.raises(TypeError) as exc_info:
        objects = composer(x=11, xy=(13, 14), yy=24, a=100, b=200, c=300)
    assert str(exc_info.value) == "build: missing required argument xx"

def test_Composer_simple_unexpected():
    composer = Composer(Alpha, Beta, Beta.build, gamma)
    with pytest.raises(TypeError) as exc_info:
        objects = composer(x=11, xy=(13, 14), xx=23, zz=45, yy=24, a=100, b=200, c=300)
    assert str(exc_info.value) == "unexpected arguments: zz=45"

def test_Composer_partial():
    composer = Composer(Alpha, Beta, Beta.build, gamma)
    arguments = dict(x=11, xy=(13, 14), xx=23, zz=45, yy=24, a=100, b=200, c=300)
    argument_store = ArgumentStore(arguments)
    objects = composer.partial(argument_store)
    _check_objects(objects)
    with pytest.raises(TypeError) as exc_info:
        composer.verify_argument_store(argument_store)
    assert str(exc_info.value) == "unexpected arguments: zz=45"

def test_Composer_sub():
    arguments = dict(x=11, xy=(13, 14), xx=23, yy=24, a=100, b=200, c=300, sub_a=111, sub_b=222, sub_c=333)
    argument_store = ArgumentStore(arguments)
    composer = Composer(Alpha, Beta, Beta.build, gamma)
    objects = composer.partial(argument_store)
    _check_objects(objects)
    sub_composer = Composer(fab, fbc)
    sub_objects = sub_composer.partial(argument_store, prefix='sub_')
    assert sub_objects[0] == [111, 222]
    assert sub_objects[1] == [222, 333]
    composer.verify_argument_store(argument_store)

def test_Composer_sub_missing():
    arguments = dict(x=11, xy=(13, 14), xx=23, yy=24, a=100, b=200, c=300, sub_a=111, sub_c=333)
    argument_store = ArgumentStore(arguments)
    composer = Composer(Alpha, Beta, Beta.build, gamma)
    objects = composer.partial(argument_store)
    _check_objects(objects)
    sub_composer = Composer(fab, fbc)
    with pytest.raises(TypeError) as exc_info:
        sub_objects = sub_composer.partial(argument_store, prefix='sub_')
    assert str(exc_info.value) == "fab: missing required argument b"

def test_Composer_sub_unexpected():
    arguments = dict(x=11, xy=(13, 14), xx=23, yy=24, zz=45, a=100, b=200, c=300, sub_a=111, sub_b=222, sub_c=333, sub_d=444)
    argument_store = ArgumentStore(arguments)
    composer = Composer(Alpha, Beta, Beta.build, gamma)
    objects = composer.partial(argument_store)
    _check_objects(objects)
    sub_composer = Composer(fab, fbc)
    sub_objects = sub_composer.partial(argument_store, prefix='sub_')
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
