.. image:: https://travis-ci.org/wtforms/wtforms-appengine.svg?branch=master
   :target: https://travis-ci.org/wtforms/wtforms-appengine
.. image:: https://coveralls.io/repos/wtforms/wtforms-appengine/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/wtforms/wtforms-appengine?branch=master

WTForms-Appengine
=================

WTForms-Appengine is a fork of the ``wtforms.ext.appengine`` package 
from WTForms. The package has been renamed to ``wtforms_appengine`` 
but otherwise should function the same as the ext package, at least
for the moment.

to install::
	
	pip install WTForms-Appengine


Rationale
---------

The reasoning for splitting out this package is that WTForms 2.0 has
deprecated all its ``wtforms.ext.<library>`` packages and they will
not receive any further feature updates. The authors feel that packages
for companion libraries work better with their own release schedule and
the ability to diverge more from WTForms.

This package is currently looking for a permanent maintainer, and if you 
wish to maintain this package please contact ``wtforms@simplecodes.com``.
