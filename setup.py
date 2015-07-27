
from setuptools import setup, find_packages
import os
import sys
import re

requires = ['setuptools']

def get_build_number():
    fname = 'build.info'
    if os.path.isfile(fname):
        with open(fname) as f:
            build_number = f.read()
            build_number = re.sub("[^a-z0-9]+","", build_number, flags=re.IGNORECASE)
            return '.' + build_number
            
    return ''

if sys.version_info[:2] < (2, 7):
    requires.append('unittest2')

here = os.path.dirname(__file__)
README = open(os.path.join(here, 'README.rst')).read()
# CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='wondermall-perfmetrics',
      version='3.0' + get_build_number(),
      author='Labgoo',
      author_email='roman@wondermall.com',
      description='Wondermall customized Send performance metrics about Python code to Statsd',
      long_description=README, # + '\n\n' + CHANGES,
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 3",
                   "License :: Repoze Public License",
                   "Topic :: System :: Monitoring",
                   ],
      url="https://github.com/Labgoo/perfmetrics",
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      tests_require=requires + ['nose'],
      test_suite="nose.collector",
      install_requires=requires,
      entry_points="""\
      [paste.filter_app_factory]
      statsd = perfmetrics:make_statsd_app
      """,
      )
