# -*- coding: utf-8 -*-

import collections
import inspect
import os

import pytest

from zirkon.validator.error import MinValueError, \
                                   MaxValueError, \
                                   MinLengthError, \
                                   MaxLengthError, \
                                   InvalidTypeError, \
                                   MissingRequiredOptionError
from zirkon.validator.int_validators import IntList, IntTuple
from zirkon.validator.float_validators import FloatList, FloatTuple
from zirkon.validator.str_validators import StrList, StrTuple
from zirkon.validator.bool_validators import BoolList, BoolTuple

def sequence(sequence_type, value, mult):
    return sequence_type(value for i in range(mult))

scenario = collections.OrderedDict()

Parameters = collections.namedtuple("Parameters", ('vclass', 'vseq', 'bseq', 'oseq', 'vscalar'))

scenario['int_list'] = Parameters(
    vclass=IntList,
    vseq=lambda *, m: sequence(list, m, m),
    bseq=lambda *, m: sequence(list, m * 1.1, m),
    oseq=lambda *, m: sequence(tuple, m, m),
    vscalar=2)

scenario['int_tuple'] = Parameters(
    vclass=IntTuple,
    vseq=lambda *, m: sequence(tuple, m, m),
    bseq=lambda *, m: sequence(tuple, m * 1.1, m),
    oseq=lambda *, m: sequence(list, m, m),
    vscalar=2)

scenario['float_list'] = Parameters(
    vclass=FloatList,
    vseq=lambda *, m: sequence(list, m * 1.1, m),
    bseq=lambda *, m: sequence(list, str(m), m),
    oseq=lambda *, m: sequence(tuple, m * 1.1, m),
    vscalar=2.4)

scenario['float_tuple'] = Parameters(
    vclass=FloatTuple,
    vseq=lambda *, m: sequence(tuple, m * 1.1, m),
    bseq=lambda *, m: sequence(list, str(m), m),
    oseq=lambda *, m: sequence(list, m * 1.1, m),
    vscalar=2.4)

scenario['str_list'] = Parameters(
    vclass=StrList,
    vseq=lambda *, m: sequence(list, str(m), m),
    bseq=lambda *, m: sequence(list, m, m),
    oseq=lambda *, m: sequence(tuple, str(m), m),
    vscalar='abc')

scenario['str_tuple'] = Parameters(
    vclass=StrTuple,
    vseq=lambda *, m: sequence(tuple, str(m), m),
    bseq=lambda *, m: sequence(tuple, m, m),
    oseq=lambda *, m: sequence(list, str(m), m),
    vscalar='abc')

scenario['bool_list'] = Parameters(
    vclass=BoolList,
    vseq=lambda *, m: sequence(list, m % 2 == 0, m),
    bseq=lambda *, m: sequence(list, m * 1.1, m),
    oseq=lambda *, m: sequence(tuple, m % 2 == 0, m),
    vscalar=True)

scenario['bool_tuple'] = Parameters(
    vclass=BoolTuple,
    vseq=lambda *, m: sequence(tuple, m % 2 == 0, m),
    bseq=lambda *, m: sequence(tuple, m * 1.1, m),
    oseq=lambda *, m: sequence(list, m % 2 == 0, m),
    vscalar=False)

@pytest.fixture(params=tuple(scenario.values()), ids=tuple(scenario.keys()))
def parameters(request):
    return request.param

def test_basic(parameters):
    iv = parameters.vclass()
    seq = parameters.vseq(m=3)
    assert len(seq) == 3
    v = iv.validate(name='alpha', defined=True, value=seq)
    assert v is seq
    seq = parameters.vseq(m=0)
    assert len(seq) == 0
    v = iv.validate(name='alpha', defined=True, value=seq)
    assert v is seq
    with pytest.raises(InvalidTypeError):
        v = iv.validate(name='alpha', defined=True, value=parameters.vscalar)
    with pytest.raises(InvalidTypeError):
        v = iv.validate(name='alpha', defined=True, value=parameters.oseq(m=3))
    with pytest.raises(InvalidTypeError):
        v = iv.validate(name='alpha', defined=True, value=parameters.bseq(m=3))
    with pytest.raises(MissingRequiredOptionError):
        v = iv.validate(name='alpha', defined=False, value=None)

def test_default(parameters):
    dseq = parameters.vseq(m=4)
    iv = parameters.vclass(default=dseq)
    seq = parameters.vseq(m=2)
    v = iv.validate(name='alpha', defined=True, value=seq)
    assert v is seq
    v = iv.validate(name='alpha', defined=False, value=None)
    assert v == dseq
    if isinstance(dseq, list):
        # check immutable default:
        assert len(dseq) == 4
        v.append(10)
        assert len(dseq) == 4
        v2 = iv.validate(name='alpha', defined=False, value=None)
        assert len(v2) == 4
        assert v2 == dseq

def test_bad_default_type_scalar(parameters):
    with pytest.raises(InvalidTypeError):
        iv = parameters.vclass(default='ten')

def test_bad_default_type_sequence(parameters):
    with pytest.raises(InvalidTypeError):
        iv = parameters.vclass(default=parameters.oseq(m=3))

def test_bad_default_item_type(parameters):
    with pytest.raises(InvalidTypeError):
        iv = parameters.vclass(default=parameters.bseq(m=3))

def test_default_min_len(parameters):
    dseq = parameters.vseq(m=4)
    iv = parameters.vclass(default=dseq, min_len=3)
    with pytest.raises(MinLengthError):
        v = iv.validate(name='alpha', defined=True, value=parameters.vseq(m=2))
    seq = parameters.vseq(m=3)
    v = iv.validate(name='alpha', defined=True, value=seq)
    assert v is seq
    v = iv.validate(name='alpha', defined=False, value=None)
    assert v == dseq

def test_bad_default_min(parameters):
    with pytest.raises(MinLengthError):
        iv = parameters.vclass(default=parameters.vseq(m=2), min_len=3)

def test_bad_default_max(parameters):
    with pytest.raises(MaxLengthError):
        iv = parameters.vclass(default=parameters.vseq(m=4), max_len=3)

def test_default_max(parameters):
    dseq = parameters.vseq(m=4)
    iv = parameters.vclass(default=dseq, min_len=3, max_len=5)
    with pytest.raises(MinLengthError):
        v = iv.validate(name='alpha', defined=True, value=parameters.vseq(m=2))
    with pytest.raises(MaxLengthError):
        v = iv.validate(name='alpha', defined=True, value=parameters.vseq(m=6))
    seq = parameters.vseq(m=3)
    v = iv.validate(name='alpha', defined=True, value=seq)
    assert v is seq
    seq = parameters.vseq(m=4)
    v = iv.validate(name='alpha', defined=True, value=seq)
    assert v is seq
    v = iv.validate(name='alpha', defined=False, value=None)
    assert v == dseq

def test_item_options(parameters):
    dseq = parameters.vseq(m=4)
    if not isinstance(dseq[0], (str, bool)):
        imin = parameters.vseq(m=4)[0]
        imax = parameters.vseq(m=5)[0]
        iv = parameters.vclass(default=dseq, min_len=3, max_len=10, item_min=imin, item_max=imax)
        with pytest.raises(MinValueError):
            v = iv.validate(name='alpha', defined=True, value=parameters.vseq(m=3))
        for m in 4, 5:
            seq = parameters.vseq(m=m)
            v = iv.validate(name='alpha', defined=True, value=seq)
            v is seq
        with pytest.raises(MaxValueError):
            v = iv.validate(name='alpha', defined=True, value=parameters.vseq(m=6))

