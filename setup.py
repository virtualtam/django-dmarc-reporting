#!/usr/bin/env python
"""Setup script for django-dmarc-reporting"""
import codecs
import os
import re

from setuptools import find_packages, setup


def get_long_description():
    """Reads the main README.rst to get the program's long description"""
    with codecs.open('README.rst', 'r', 'utf-8') as f_readme:
        return f_readme.read()


def get_program_metadata(attribute):
    """Reads program metadata from the main package's __init__"""
    with open(os.path.join('dmarc_reporting', '__init__.py'), 'r') as f_init:
        return re.search(
            r'^__{attr}__\s*=\s*[\'"]([^\'"]*)[\'"]'.format(attr=attribute),
            f_init.read(), re.MULTILINE
        ).group(1)


setup(
    name=get_program_metadata('title'),
    version=get_program_metadata('version'),
    description="Automated DMARC report processing",
    long_description=get_long_description(),
    author=get_program_metadata('author'),
    author_email='virtualtam@flibidi.net',
    license='BSD',
    url='https://github.com/virtualtam/django-dmarc-reporting',
    keywords="django dmarc mail report",
    packages=find_packages(exclude=['tests.*', 'tests']),
    install_requires=[
        'django>=2.0,<2.1',
        'xmltodict>=0.11,<0.12',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
    ])
