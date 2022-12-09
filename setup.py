#!/usr/bin/env python
import os
import sys
import shutil

from pipelines import __version__, __author__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# NOTE:
# do not edit install_requires and dependency_links manually
# please use pipenv to install packages, then make sync-requirements
# to sync into setup.py

setup(
    name='pipelines',
    version=__version__,
    description='Pipelines',
    url='https://github.com/Wiredcraft/pipelines',
    author=__author__,
    author_email='info@wiredcraft.com',
    license='MIT',
    package_dir={
        'pipelines': 'pipelines',
    },
    package_data={
        'pipelines.api': [
            'app_dist/*.html',
            'app_dist/client/dist/*',
            'templates/*.html']},
    packages=[
        'pipelines',
        'pipelines.pipeline',
        'pipelines.api',
        'pipelines.plugins',
        'pipelines.plugin'],
    entry_points={
        'console_scripts': [
            'pipelines = pipelines.cli:main',
        ],
    },
    install_requires=[
        "certifi==2022.12.7; python_version >= '3.6'",
        "charset-normalizer==2.0.12; python_version >= '3'",
        'coloredlogs==15.0.1',
        "contextlib2==21.6.0; python_version >= '3.6'",
        'docopt==0.6.2',
        'dotmap==1.3.26',
        'filelock==3.4.0',
        "humanfriendly==10.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "idna==3.3; python_version >= '3'",
        'jinja2==3.0.3',
        "markupsafe==2.1.1; python_version >= '3.7'",
        'pyyaml==6.0',
        'requests==2.26.0',
        'schema==0.7.5',
        'sh==1.14.2',
        'tornado==6.1',
        "urllib3==1.26.9; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'"],
    dependency_links=[],
)
