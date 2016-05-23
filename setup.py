#!/usr/bin/env python
import os
import sys
import shutil

from pipelines import __version__, __author__

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
        'pipelines': 'pipelines',
    },
    packages=[
        'pipelines',
        'pipelines.pipeline',
        'pipelines.api',
        'pipelines.plugins',
        'pipelines.plugin'
    ],
    scripts=[
        'bin/pipelines'
    ],
    install_requires = [],
)
