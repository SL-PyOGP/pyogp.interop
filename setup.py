"""
@file setup.py
@date 2008-09-16
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='pyogp.interop',
      version=version,
      description="The Open Grid Protocol Test Harness",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='pyogp ogp awg testharness virtualworlds testing',
      author='Architecture Working Group, pyogp Taskforce',
      author_email='pyogp@lists.secondlife.com',
      url='http://pyogp.net',
      license='Apache License V2.0',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pyogp'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'indra.ipc',
          'indra.base',
          'pyogp.lib.base'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
