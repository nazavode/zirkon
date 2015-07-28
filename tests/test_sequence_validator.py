# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from config.validator.error import InvalidOptionValidationError, \
                                   MinValidationError, \
                                   MaxValidationError, \
                                   MinLenValidationError, \
                                   MaxLenValidationError, \
                                   TypeValidationError, \
                                   UndefinedKeyValidationError
from config.validator.int_validator import IntListValidator, \
                                           IntTupleValidator
from config.validator.float_validator import FloatListValidator, \
                                             FloatTupleValidator
from config.validator.str_validator import StrListValidator, \
                                           StrTupleValidator
from config.validator.bool_validator import BoolListValidator, \
                                            BoolTupleValidator

from common.test_scenarios import pytest_generate_tests
    
def sequence(sequence_type, value, mult):
    return sequence_type(value for i in range(mult))

class TestSequenceWithScenarios(object):
    scenario_int_list = ('int_list',
        dict(vclass=IntListValidator,
             vseq=lambda *, m: sequence(list, m, m),
             bseq=lambda *, m: sequence(list, m * 1.1, m),
             oseq=lambda *, m: sequence(tuple, m, m),
             vscalar=2,
        ))
    scenario_int_tuple = ('int_tuple',
        dict(vclass=IntTupleValidator,
             vseq=lambda *, m: sequence(tuple, m, m),
             bseq=lambda *, m: sequence(tuple, m * 1.1, m),
             oseq=lambda *, m: sequence(list, m, m),
             vscalar=2,
        ))
    scenario_float_list = ('float_list',
        dict(vclass=FloatListValidator,
             vseq=lambda *, m: sequence(list, m * 1.1, m),
             bseq=lambda *, m: sequence(list, str(m), m),
             oseq=lambda *, m: sequence(tuple, m * 1.1, m),
             vscalar=2.4,
        ))
    scenario_float_tuple = ('float_tuple',
        dict(vclass=FloatTupleValidator,
             vseq=lambda *, m: sequence(tuple, m * 1.1, m),
             bseq=lambda *, m: sequence(list, str(m), m),
             oseq=lambda *, m: sequence(list, m * 1.1, m),
             vscalar=2.4,
        ))
    scenario_str_list = ('str_list',
        dict(vclass=StrListValidator,
             vseq=lambda *, m: sequence(list, str(m), m),
             bseq=lambda *, m: sequence(list, m, m),
             oseq=lambda *, m: sequence(tuple, str(m), m),
             vscalar='abc',
        ))
    scenario_str_tuple = ('str_tuple',
        dict(vclass=StrTupleValidator,
             vseq=lambda *, m: sequence(tuple, str(m), m),
             bseq=lambda *, m: sequence(tuple, m, m),
             oseq=lambda *, m: sequence(list, str(m), m),
             vscalar='abc',
        ))
    scenario_bool_list = ('bool_list',
        dict(vclass=BoolListValidator,
             vseq=lambda *, m: sequence(list, m % 2 == 0, m),
             bseq=lambda *, m: sequence(list, m * 1.1, m),
             oseq=lambda *, m: sequence(tuple, m % 2 == 0, m),
             vscalar=True,
        ))
    scenario_bool_tuple = ('bool_tuple',
        dict(vclass=BoolTupleValidator,
             vseq=lambda *, m: sequence(tuple, m % 2 == 0, m),
             bseq=lambda *, m: sequence(tuple, m * 1.1, m),
             oseq=lambda *, m: sequence(list, m % 2 == 0, m),
             vscalar=False,
        ))
    scenarios = (scenario_int_list, scenario_int_tuple,
                 scenario_float_list, scenario_float_tuple,
                 scenario_str_list, scenario_str_tuple,
                 scenario_bool_list, scenario_bool_tuple,
    )

    def test_basic(self, vclass, vseq, bseq, oseq, vscalar):
        iv = vclass()
        seq = vseq(m=3)
        assert len(seq) == 3
        v = iv.validate(key='alpha', defined=True, value=seq)
        assert v is seq
        seq = vseq(m=0)
        assert len(seq) == 0
        v = iv.validate(key='alpha', defined=True, value=seq)
        assert v is seq
        with pytest.raises(TypeValidationError):
            v = iv.validate(key='alpha', defined=True, value=vscalar)
        with pytest.raises(TypeValidationError):
            v = iv.validate(key='alpha', defined=True, value=oseq(m=3))
        with pytest.raises(TypeValidationError):
            v = iv.validate(key='alpha', defined=True, value=bseq(m=3))
        with pytest.raises(UndefinedKeyValidationError):
            v = iv.validate(key='alpha', defined=False, value=None)

    def test_default(self, vclass, vseq, bseq, oseq, vscalar):
        dseq = vseq(m=4)
        iv = vclass(default=dseq)
        seq = vseq(m=2)
        v = iv.validate(key='alpha', defined=True, value=seq)
        assert v is seq
        v = iv.validate(key='alpha', defined=False, value=None)
        assert v == dseq
        if isinstance(dseq, list):
            # check immutable default:
            assert len(dseq) == 4
            v.append(10)
            assert len(dseq) == 4
            v2 = iv.validate(key='alpha', defined=False, value=None)
            assert len(v2) == 4
            assert v2 == dseq
    
    def test_bad_default_type_scalar(self, vclass, vseq, bseq, oseq, vscalar):
        with pytest.raises(TypeValidationError):
            iv = vclass(default='ten')
    
    def test_bad_default_type_sequence(self, vclass, vseq, bseq, oseq, vscalar):
        with pytest.raises(TypeValidationError):
            iv = vclass(default=oseq(m=3))

    def test_bad_default_item_type(self, vclass, vseq, bseq, oseq, vscalar):
        with pytest.raises(TypeValidationError):
            iv = vclass(default=bseq(m=3))
    
    def test_default_min_len(self, vclass, vseq, bseq, oseq, vscalar):
        dseq = vseq(m=4)
        iv = vclass(default=dseq, min_len=3)
        with pytest.raises(MinLenValidationError):
            v = iv.validate(key='alpha', defined=True, value=vseq(m=2))
        seq = vseq(m=3)
        v = iv.validate(key='alpha', defined=True, value=seq)
        assert v is seq
        v = iv.validate(key='alpha', defined=False, value=None)
        assert v == dseq
    
    def test_bad_default_min(self, vclass, vseq, bseq, oseq, vscalar):
        with pytest.raises(MinLenValidationError):
            iv = vclass(default=vseq(m=2), min_len=3)
    
    def test_bad_default_max(self, vclass, vseq, bseq, oseq, vscalar):
        with pytest.raises(MaxLenValidationError):
            iv = vclass(default=vseq(m=4), max_len=3)
    
    def test_default_max(self, vclass, vseq, bseq, oseq, vscalar):
        dseq = vseq(m=4)
        iv = vclass(default=dseq, min_len=3, max_len=5)
        with pytest.raises(MinLenValidationError):
            v = iv.validate(key='alpha', defined=True, value=vseq(m=2))
        with pytest.raises(MaxLenValidationError):
            v = iv.validate(key='alpha', defined=True, value=vseq(m=6))
        seq = vseq(m=3)
        v = iv.validate(key='alpha', defined=True, value=seq)
        assert v is seq
        seq = vseq(m=4)
        v = iv.validate(key='alpha', defined=True, value=seq)
        assert v is seq
        v = iv.validate(key='alpha', defined=False, value=None)
        assert v == dseq

    def test_item_options(self, vclass, vseq, bseq, oseq, vscalar):
        dseq = vseq(m=4)
        if not isinstance(dseq[0], (str, bool)):
            imin = vseq(m=4)[0]
            imax = vseq(m=5)[0]
            iv = vclass(default=dseq, min_len=3, max_len=10, item_min=imin, item_max=imax)
            with pytest.raises(MinValidationError):
                v = iv.validate(key='alpha', defined=True, value=vseq(m=3))
            for m in 4, 5:
                seq = vseq(m=m)
                v = iv.validate(key='alpha', defined=True, value=seq)
                v is seq
            with pytest.raises(MaxValidationError):
                v = iv.validate(key='alpha', defined=True, value=vseq(m=6))

