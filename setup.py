#!/usr/bin/env python3.6

from setuptools import setup

setup(name='Pathfinder',
      version='2.0',
      description='''A python version of the Pathfinder project created to be used with the
                    University of Tennessee IEEE Robotics team\'s RIP system''',
      url='https://github.com/utk-robotics-2017/pathfinder_python',
      author='UTK IEEE Robotics Team (Volts)',
      packages=['.'],
      install_requires=[
          'tornado',
          'numpy',
          'flake8'
      ])
