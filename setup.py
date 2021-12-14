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
    author_email='info@wiredcraft.com',
    license='MIT',
    package_dir={ 
        'pipelines': 'pipelines',
    },
    package_data={
        'pipelines.api': ['app_dist/*.html', 'app_dist/client/dist/*', 'templates/*.html']
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
    install_requires = [
        'futures==2.2.0',
        'Jinja2==3.0.3',
        'PyYAML==6.0',
        'requests==2.26.0',
        'sh==1.14.2',
        'tornado==6.1',
        'docopt==0.6.2',
        'dotmap==1.3.26',
        'schema==0.7.5',
        'filelock==3.4.0'
    ],
)
