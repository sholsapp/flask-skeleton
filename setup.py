#!/usr/bin/env python

import os

from setuptools import setup

README = None
with open(os.path.abspath('README.md')) as fh:
    README = fh.read()

setup(
  name='flask-skeleton',
  version='0.1.0',
  description=README,
  author='Stephen Holsapple',
  author_email='sholsapp@gmail.com',
  url='http://www.flask.com',
  packages=['flaskskeleton'],
  install_requires=[
    'Flask',
    'configobj',
    'Flask-Bootstrap',
    'Flask-Script',
    'Flask-SQLAlchemy',
    'Flask-Restless',
  ],
)
