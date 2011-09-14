#!/usr/bin/env python

import glob
from setuptools import setup, find_packages

version = '0.3'

setup(name='porkchop',
  version=version,
  description='Porkchop is a simple HTTP-based dictionary server',
  long_description='Porkchop is a simple HTTP-based dictionary server',
  classifiers=[],
  keywords='',
  author='Scott Smith',
  author_email='scott@disqus.com',
  url='http://github.com/disqus/porkchop',
  license='Apache 2.0',
  packages=find_packages(),
  include_package_data=True,
  zip_safe=False,
  install_requires=[],
  entry_points={
    'console_scripts': [
      'porkchop = porkchop.commandline:main'
      'porkchop-collector = porkchop.commandline:collector'
    ],
  },
  data_files=[
    ('/usr/share/porkchop/plugins', glob.glob('share/plugins/*.py'))
  ]
)
