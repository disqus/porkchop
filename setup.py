#!/usr/bin/env python

import glob
from setuptools import setup, find_packages

version = '0.7.3'

setup(name='porkchop',
  version=version,
  description='Porkchop is a simple HTTP-based system information server',
  long_description='Porkchop is a simple HTTP-based system information server',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: Apache Software License',
    'Topic :: System :: Networking :: Monitoring'
  ],
  keywords='',
  author='Scott Smith',
  author_email='scott@disqus.com',
  url='http://github.com/disqus/porkchop',
  license='Apache 2.0',
  packages=find_packages(),
  include_package_data=True,
  zip_safe=False,
  install_requires=['requests', 'setuptools'],
  entry_points={
    'console_scripts': [
      'porkchop = porkchop.commandline:main',
      'porkchop-collector = porkchop.commandline:collector'
    ],
  }
)
