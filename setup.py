#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: i@wangtai.me


from setuptools import setup, find_packages

try:
    long_description = open('README.md').read()
except:
    long_description = ''

setup(
    name='umeng_push',
    version='0.4',
    packages=find_packages(),
    author='WANG Tai',
    author_email='i@wangtai.me',
    url='',
    description='UMeng Push Service Python API',
    long_description=long_description,
    license='Apache2',
    requires=[
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: System :: Installation/Setup'
    ],
    include_package_data=True,
    zip_safe=False
)
