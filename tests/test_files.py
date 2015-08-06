# -*- coding: utf-8 -*-

import os

import pytest

from daikon.toolbox import files


def test_createdir(tmpdir):
    #assert os.path.exists(tmpdir.strpath)
    #assert os.path.isdir(tmpdir.strpath)
    tdir = os.path.join(tmpdir.strpath, 'xyz')
    assert not os.path.exists(tdir)
    ttdir = os.path.join(tdir, 'abc')
    assert not os.path.exists(ttdir)
    tfile = os.path.join(ttdir, 'a.txt')
    files.createdir(tfile)
    assert os.path.isdir(ttdir)
    assert os.path.isdir(tdir)
