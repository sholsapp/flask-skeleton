#!/usr/bin/env python

from setuptools import setup, find_packages
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
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
     package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.html"],
    },
    install_requires=[
        'APScheduler',
        'Flask',
        'Flask-Bootstrap',
        'Flask-Cors',
        'Flask-REST-JSONAPI',
        'Flask-SQLALchemy',
        'Flask-Security',
        'backoff',
        'configobj',
        'gunicorn',
    ],
    entry_points = {
        'console_scripts': [
            'flask-skeleton-worker=flaskskeleton.worker:main',
        ],
    }
)
