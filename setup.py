#!/usr/bin/env python
import os
import sys
import shutil

# from shazam import __version__, __author__
__version__ = '0.0.1'
__author__ = 'Wirecraft'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pipelines',
    version=__version__,
    description='Pipelines',
    url = 'https://getpipelines.com',
    author=__author__,
    author_email='pipelines@wirecraft.com',
    license='MIT',
    package_dir={ 
        'pipelines': 'lib',
    },
    packages=[
        'pipelines',
        'pipelines.pipeline',
        'pipelines.api',
        'pipelines.plugins',
        'pipelines.plugin'
    ],
    scripts=[
        'bin/pipelines-api'
    ],
    install_requires = [],
)
