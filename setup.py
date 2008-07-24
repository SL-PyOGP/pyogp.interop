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
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
