import sys

extra = {}

try:
    from setuptools import setup
    has_setuptools = True
    extra['test_suite'] = 'tests.tests'
    extra['install_requires'] = ['WTForms>=1.0.5']
    extra['extras_require'] = {
    }
except ImportError:
    from distutils.core import setup
    has_setuptools = False

if sys.version_info >= (3,) and not has_setuptools:
    raise Exception('Python 3 support requires setuptools.')

setup(
    name='WTForms-Appengine',
    version='0.1dev',
    url='http://github.com/wtforms/wtforms-appengine/',
    license='BSD',
    author='Thomas Johansson, James Crasta',
    author_email='wtforms@simplecodes.com',
    description='Appengine tools for WTForms',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=[
        'wtforms_appengine',
    ],
    package_data={
    },
    **extra
)
