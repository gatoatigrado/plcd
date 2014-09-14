# -*- coding: utf-8 -*-
"""
Represents a compression scheme. This is an informational blurb that specifies
how to compress / decompress data. For example, if your compressor has been
pre-loaded with data X, the decompressor must know about X to decompress any
messages.
"""
from __future__ import absolute_import
from __future__ import print_function

import zlib


PLCD_SCHEME_JSON_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {'type': ['string', 'null']},

        'base_compressor': {
            'enum': ['zlib']
        },

        'base_compressor_settings': {
            'type': 'object',
            'properties': {
                'level': {'type': 'int'}
            },
            'additionalProperties': False,
        },

        # preloaded data, in compressed form
        'preloaded_compressed_base64': {'type': 'string'},

        'preloaded_compressed_md5_hash_base64': {'type': 'string'},
    },
    'required': [
        'name',
        'preloaded_compressed_base64',
        'base_compressor'
    ],
    'additionalProperties': False,
}


class ZlibPlcdScheme(object):
    """
    Compresses data with `zlib` as the base compressor.
    """

    def __init__(self, name, uncompressed_data_to_preload, level=None):
        """
        Initializes the compressor. Usually, you'll want to use a
        helper method that reads a description blurb based on
        PLCD_SCHEME_JSON_SCHEMA.

        :param name: Name of the compressor, or None to disable version tags
        :type name: str or None

        :param uncompressed_data_to_preload:
            data you wish to seed the compressor with
        :type uncompressed_data_to_preload: str

        :param level: zlib compression level, or None to use the default
        :type level: int or None
        """
        self.name = str(name) if name is not None else None
        self.name_tag = str(name) + ':' if name is not None else ''

        _compressobj = zlib.compressobj(*([level] if level else []))
        _decompressobj = zlib.decompressobj()

        assert isinstance(uncompressed_data_to_preload, str)
        _decompressobj.decompress(
            _compressobj.compress(uncompressed_data_to_preload) +
            _compressobj.flush(zlib.Z_SYNC_FLUSH)
        )

        # To prevent bugs, we don't let anyone actually access
        # _new_compressor / _new_decompressor
        self._new_decompressor = _decompressobj.copy
        self._new_compressor = _compressobj.copy

    def compress(self, datum):
        """
        Compresses data using the pre-loaded dictionary

        :param datum: input data, already encoded into a string
        :type datum: str
        :return: compressed data, prepended with a tag
        :rtype: str
        """
        assert isinstance(datum, str), \
            "Please do any data-->string encoding before compression."
        compressor = self._new_compressor()
        return (
            self.name_tag +
            compressor.compress(datum) +
            compressor.flush(zlib.Z_SYNC_FLUSH)
        )

    def decompress(self, datum):
        """
        Decompresses data using the pre-loaded dictionary

        :param datum: compressed data, prepended with a tag
        :type datum: str
        :return: decompressed data, with the tag stripped
        :rtype: str
        """
        if not datum.startswith(self.name_tag):
            # NOTE: expect tags < 20 chars
            real = (
                datum[:datum[:20].index(':')]
                if ':' in datum[:20]
                else None
            )
            raise ValueError(
                "Mismatched scheme tag (got {0}, expecting {1})!".format(real, self.name)
            )
        datum = datum[len(self.name_tag):]
        return self._new_decompressor().decompress(datum)
