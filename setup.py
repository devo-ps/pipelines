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
        'futures==3.0.5',
        'Jinja2==2.8',
        'PyYAML==3.11',
        'requests==2.9.1',
        'sh==1.11',
        'tornado==4.3',
        'docopt==0.6.2',
        'dotmap==1.1.16',
        'schema==0.5.0',
        'filelock==2.0.6'
    ],
)
