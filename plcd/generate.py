# -*- coding: utf-8 -*-
"""
Searches for the best pre-loading data. Currently just a very simple routine;
we'll try more complicated things if/when necessary.
"""
from __future__ import absolute_import
from __future__ import print_function

import fileinput
import json
import logging
import optparse
import random
from operator import itemgetter

import plcd.scheme


def _get_n_samples(num_samples):
    """
    Splits a list of data into a pre-loading set and evaluation set.

    :param num_samples: number of elements ot use for pre-loading
    :type num_samples: int
    :return: function taking data and splitting it into pre-loading and evaluation
    :rtype: (tuple[α] --> tuple[α], tuple[α])
    """
    def inner(data):
        """Inner function (see outer docstring)"""
        data = list(data)
        assert num_samples <= len(data), \
            "Not enough sample data (expected at least {0} elements)".format(num_samples)
        sample = []
        for _ in xrange(num_samples):
            idx = random.randint(0, len(data) - 1)
            sample.append(data.pop(idx))
        return tuple(sample), tuple(data)
    return inner


def iterate_until_converged(lazy_iter, key_fcn=itemgetter(0), batch_size=10):
    """
    Iterates until "converged". Convergence is when we get a sequence of
    `batch_size` values which are worse than the best we've seen so far.

    :param lazy_iter:
        iterator yielding score-able values, usually (score, thing_being_scored)
    :type lazy_iter: iterable[α]
    :param key_fcn: Function mapping `lazy_iter` values to comparable items
    :type key_fcn: Ord β => α -> β
    :param batch_size:
        How many to try at once, since if we have a random process we probably
        don't want to just stop when the next one is worse.
    :type batch_size: int
    :return: best value
    :rtype: α
    """
    current_best = next(lazy_iter)
    while True:
        next_best = max(tuple(next(lazy_iter) for _ in xrange(batch_size)), key=key_fcn)
        if key_fcn(next_best) > key_fcn(current_best):
            current_best = next_best
        else:
            return current_best


def evaluate_zlib(name, preload, test):
    """
    Runs pre-loaded compression on a sample, returns the compression ratio.

    :param name: tag for the compressor
    :type name: str
    :param preload: data for pre-loading
    :type preload: str
    :param test: data samples to evaluate the compressor
    :type test: iterable[str]
    :returns: tuple (score, scheme)
    :rtype: tuple
    """
    scheme = plcd.scheme.ZlibPlcdScheme(name, preload)
    uncompressed_len = sum(len(datum) for datum in test)
    compressed_len = sum(len(scheme.compress(datum)) for datum in test)
    return (float(uncompressed_len) / compressed_len), scheme


def generate_simple(name, data, get_sample_fcn=_get_n_samples(3)):
    """
    Simple scheme generation function. We'll make something more complicated (GAs
    might work) if/when there's a real use case.

    :param name: tag for the compressor
    :type name: str
    :param data: sample data elements
    :type data: iterable[str]
    :param get_sample_fcn:
        function which will draw a sample of data
    :type get_sample_fcn:
        iterable[str] --> (tuple[str], tuple[str])
    :returns: the best scoring model (the compression ratio and the model)
    :rtype: tuple (score, scheme)
    """
    data = tuple(data)
    eval_fcn = lambda (preload, test): evaluate_zlib(
        name,
        ''.join(preload),
        test
    )
    ratio, scheme = iterate_until_converged(
        eval_fcn(get_sample_fcn(data))
        for _ in xrange(int(1e6))
    )
    logging.info("Best ratio: {0}".format(ratio))
    return ratio, scheme


def main(args=None):
    """
    Main entry point for command-line execution

    :param args: string command line args (or None)
    """
    cmd_args = optparse.OptionParser()
    cmd_args.add_option(
        "--name",
        help="name / tag for the encoder (e.g. user_v1)"
    )
    cmd_args.add_option(
        "--input-lines",
        dest="input_type",
        action="store_const",
        const="lines"
    )
    cmd_args.add_option(
        "--preload-with-num-samples",
        help="Select this many lines of data as pre-loading"
    )
    options, args = cmd_args.parse_args(args=args)
    logging.basicConfig(level=logging.INFO)

    if not options.input_type:
        cmd_args.error("You need to specify an input type (e.g. --input-lines)")

    if options.input_type == "lines":
        data = tuple(fileinput.input(files=args, openhook=fileinput.hook_compressed))

    if options.preload_with_num_samples is None:
        _, scheme = generate_simple(options.name, data)
    else:
        _, scheme = generate_simple(
            options.name,
            data,
            get_sample_fcn=_get_n_samples(int(options.preload_with_num_samples))
        )

    print(json.dumps(scheme.json_description_dict()))
