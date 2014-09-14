from setuptools import find_packages
from setuptools import setup


setup(
    name="plcd",
    version="0.1.0",
    provides=["plcd"],
    author="gatoatigrado",
    author_email="gatoatigrado@gmail.com",
    url="https://github.com/gatoatigrado/plcd",
    description=(
        'This is a python library for facilitating '
        'pre-loaded compression dictionary usage.'
    ),
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
    ],
    install_requires=[],
    packages=find_packages(exclude=['tests*']),
    long_description="""Facilitates use of pre-loaded compression dictionaries.

Pre-loaded compression means that you "seed" a compressor with some
sample data, which is representative of future data you wish to encode.
This is primarily useful for encoding small messages, which have repeated
information with some sample small messages.
"""
)
