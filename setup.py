#!/usr/bin/env python

from distutils.core import setup

setup(name='hetzner-dyndns',
      version='0.1',
      description='Use Hetzner DNS as a dyndns target',
      author='Benjamin Hanzelmann',
      author_email='benjamin@hanzelmann.de',
      scripts=['./hetzner-dyndns.py'],
      install_requires=['loguru', 'requests'],
      python_requires='>=3'
     )
