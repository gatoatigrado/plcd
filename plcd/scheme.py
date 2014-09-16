# -*- coding: utf-8 -*-
"""
Represents a compression scheme. This is an informational blurb that specifies
how to compress / decompress data. For example, if your compressor has been
pre-loaded with data X, the decompressor must know about X to decompress any
messages.
"""
from __future__ import absolute_import
from __future__ import print_function

import base64
import logging
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

        self.level = level

        _compressobj = zlib.compressobj(*([level] if level else []))
        _decompressobj = zlib.decompressobj()

        assert isinstance(uncompressed_data_to_preload, str)
        self.preloaded_compressed = (
            _compressobj.compress(uncompressed_data_to_preload) +
            _compressobj.flush(zlib.Z_SYNC_FLUSH)
        )
        _decompressobj.decompress(self.preloaded_compressed)

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

    def json_description_dict(self):
        """
        Generates a dictionary corresponding to PLCD_SCHEME_JSON_SCHEMA.

        :return: description of the compressor sufficient to recreate it
        :rtype: dict
        """
        return {
            'name': self.name,
            'base_compressor': 'zlib',
            'base_compressor_settings': {
                'level': self.level,
            },
            'preloaded_compressed_base64': base64.b64encode(self.preloaded_compressed),
        }

    @classmethod
    def from_json_description_dict(cls, schema):
        """
        Re-creates a compressor from json_description_dict().

        :param schema: dictionary conforming to PLCD_SCHEME_JSON_SCHEMA
        :type schema: dict
        :returns: compressor
        :rtype: ZlibPlcdScheme
        """
        try:
            # pylint: disable=import-error
            import jsonschema
        except ImportError:
            logging.warning("Install jsonschema to validate the schema.")
        else:
            jsonschema.validate(schema, PLCD_SCHEME_JSON_SCHEMA)

        compressed = base64.b64decode(
            schema['preloaded_compressed_base64']
        )
        return cls(
            name=schema['name'],
            uncompressed_data_to_preload=(
                zlib.decompressobj().decompress(compressed)
            ),
            level=schema['base_compressor_settings']['level']
        )
