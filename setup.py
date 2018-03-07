#!/usr/bin/env python

import sys
from os import path, walk
from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        name='Orange3-Tarantool',
        version='0.0.1.dev9',
        description='Tarantool Connector for Orange3.',
        long_description=open(path.join(path.dirname(__file__), 'README.md')).read(),
        license='GPL',
        packages=['rvncerr.orange3.tarantool', 'rvncerr.orange3.tarantool.widgets'],
        package_data={'rvncerr.orange3.tarantool.widgets': ['icons/*']},
        data_files=[],
        install_requires=['Orange3', 'tarantool'],
        entry_points={'orange3.addon': ('Tarantool = rvncerr.orange3.tarantool'), 'orange.widgets': ('Tarantool = rvncerr.orange3.tarantool.widgets')},
        keywords=('orange3 add-on'),
        include_package_data=True,
        zip_safe=False,
        author='Dmitriy Kalugin-Balashov',
        author_email='rvncerr@rvncerr.org',
        url='https://github.com/rvncerr/orange3-tarantool'
    )
