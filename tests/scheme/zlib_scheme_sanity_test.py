# -*- coding: utf-8 -*-
"""
Tests some really basic stuff
"""
from __future__ import absolute_import
from __future__ import print_function
import json
import zlib
import pytest

from plcd.scheme import ZlibPlcdScheme


_stable_json_dump = lambda x: json.dumps(x, sort_keys=True)


def test_compress_and_decompress():
    """Test that decompress(compress(x)) == x."""
    scheme = ZlibPlcdScheme('hi', 'fandangle')
    for input_str in ('catfood', 'fandangle2'):
        compressed = scheme.compress(input_str)
        assert scheme.decompress(compressed) == input_str


def test_compression_is_better_basic():
    """Checks that PLCD is better than nothing or vanilla
    zlib for a basic input case.
    """
    preload, test_input = map(_stable_json_dump, [
        {'a': 123, 'b': 44, 'c': 92},
        {'a': 42, 'b': 44, 'c': 91},
    ])
    scheme = ZlibPlcdScheme('x_v1', preload)

    assert len(test_input) == 27
    assert len(zlib.compress(test_input)) == 30
    assert len(scheme.compress(test_input)) == 20


def test_raises_if_bad_tag():
    """Check that assertions are raised if compressed data isn't tagged."""
    scheme = ZlibPlcdScheme('x_v1', '')
    with pytest.raises(ValueError):
        scheme.decompress('')
