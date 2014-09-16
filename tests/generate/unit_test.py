# -*- coding: utf-8 -*-
"""
Unit tests for generate.py
"""
from __future__ import absolute_import
from __future__ import print_function
import zlib

import plcd.generate
from plcd.scheme import ZlibPlcdScheme


def test_iterate_until_converged_batch_size():
    best, = plcd.generate.iterate_until_converged(iter(
        [(1,)] + [(0,)] * 3
    ), batch_size=3)
    assert best == 1


def test_iterate_until_converged_const_value_and_attached_data():
    best, token = plcd.generate.iterate_until_converged(iter(
        [(0, NotImplemented)] * 4
    ), batch_size=3)
    assert best == 0
    assert token is NotImplemented


def test_iterate_until_converged_long():
    """More realistic test that has many batches."""
    input_values = [(x // 3,) for x in xrange(1000)] + [(0,)] * 10
    best, = plcd.generate.iterate_until_converged(iter(input_values))
    assert best == 333  # 999 / 3


def test_samples_are_compressed_separately():
    together_score, _ = plcd.generate.evaluate_zlib('hi_v1', 'foobar', ['baz' * 40])
    separate_score, _ = plcd.generate.evaluate_zlib('hi_v1', 'foobar', ['baz'] * 40)

    assert together_score > 7
    assert separate_score < 1


def test_generate_with_crappy_sampler():
    score, model = plcd.generate.generate_simple(
        name='hi_v1',
        data=(),
        get_sample_fcn=lambda _: (['foobar'], ['baz'] * 40)
    )
    assert score == 0.2
    assert isinstance(model, ZlibPlcdScheme)


def test_generate_obvious_answer():
    score, model = plcd.generate.generate_simple(
        'hi_v1',
        ['baz'] + ['catfood-fandangle-zanzibar'] * 30,
        plcd.generate._get_n_samples(1)
    )
    assert score > 1.5
    chosen_preload_data = zlib.decompressobj().decompress(model.preloaded_compressed)
    assert chosen_preload_data == 'catfood-fandangle-zanzibar'
