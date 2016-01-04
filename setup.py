from codecs import open
from setuptools import setup, find_packages

setup(
    name='WTForms-Appengine',
    version='0.1',
    url='http://github.com/wtforms/wtforms-appengine/',
    license='BSD',
    author='Thomas Johansson, James Crasta',
    author_email='wtforms@simplecodes.com',
    description='Appengine fields and form generation for WTForms',
    long_description=open('README.rst', 'r', 'utf8').read(),
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
    packages=find_packages(),
    package_data={
    },
    install_requires=['WTForms>=1.0.5'],
    extras_require={
    },
    test_suite='nose.collector',
    tests_require=['nose'],
)
