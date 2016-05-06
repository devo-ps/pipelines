# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='plines',
    version='0.1.0',
    author=u'Juha Suomalainen',
    author_email='none@none.com',
    packages=[
       'pipelineplugins',
       'pipelineworm',
       'pluginworm',
    ],
    package_dir={
        '': 'lib'
    },
    scripts=[ 'scripts/pline'],
    url='http://bitbucket.org/bruno/django-geoportail',
    license='Proprietary Wiredcraft',
    description='Tool to run pipelines',
    long_description=open('README.md').read(),
    install_requires=[
          'docopt', 'PyYAML', 'requests', 'sh'
      ],
)