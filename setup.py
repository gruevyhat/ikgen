#!/usr/bin/python

from distutils.core import setup

setup(
    name='ikgen',
    version='0.0.1',
    author='gvh',
    author_email='gruevyhat@gmail.com',
    description='Character generation utility for the Iron Kingdoms RPG.',
    license='http://www.gnu.org/licenses/gpl-2.0.html',
    platforms=['any'],
    url='https://github.com/gruevyhat/ikgen',
    keywords=['character generator', 'RPG', 'iron kingdoms'],
    packages=['ikgen'],
    package_data={'ikgen': ['data/*.csv']},
    scripts=['ikg'],
)
