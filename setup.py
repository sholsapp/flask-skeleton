#!/usr/bin/env python

from setuptools import setup
import os


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
    # These are in requirements.txt.
    install_requires=[],
    entry_points = {
        'console_scripts': [
            'flask-skeleton-worker=flaskskeleton.worker:main',
        ],
    }
)
