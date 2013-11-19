#!/usr/bin/env python

from setuptools import setup

import os
def read(fname):
     return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='wtforms-ndb',
     version='0.0.1',
     description='Wtforms mapper for Appengine\'s NDB library.',
     long_description=read('README.md'),
     author='Chris Targett',
     author_email='chris@xlevus.net',
     url='http://github.com/xlevus/wtforms-ndb',
     packages=['wtforms_ndb'],
     install_requires = ['WTForms>=1.0.5'],
     classifiers=[
     ],
     keywords='',
     license='',

)
