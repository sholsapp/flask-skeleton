#!/usr/bin/env python

from setuptools import setup, find_packages
import pathlib


VERSION = "0.0.0"
with open(pathlib.Path("VERSION").resolve()) as fh:
    VERSION = fh.read().strip()


README = None
with open(pathlib.Path('README.md').resolve()) as fh:
    README = fh.read()


setup(
    name='flask-skeleton',
    version=VERSION,
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
    extras_require={
        'testing': [
            'black',
            'flake8',
            'isort',
            'mypy',
            'pytest',
            'pytest-flask',
            'types-setuptools',
        ]
    },
    entry_points={
        'console_scripts': [
            'flask-skeleton-worker=flaskskeleton.worker:main',
        ],
    }
)
