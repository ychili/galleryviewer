"""Test backports module."""

import contextlib
import sys

import pytest

import galleryviewer.backports


def test_nullcontextmanager():
    new_object = object()
    with galleryviewer.backports.NullContextManager(enter_result=new_object) as obj_in:
        assert obj_in is new_object


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
def test_equivalent_nullcontextmanager():
    new_object = object()
    cm_stdlib = contextlib.nullcontext(enter_result=new_object)
    cm_backports = galleryviewer.backports.NullContextManager(enter_result=new_object)
    with cm_stdlib as result_stdlib, cm_backports as result_backports:
        assert result_stdlib is result_backports
