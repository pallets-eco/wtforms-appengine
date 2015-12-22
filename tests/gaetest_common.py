"""
This contains common tools for gae tests, and also sets up the environment.

It should be the first import in the unit tests.
"""
# -- First setup paths
import sys
import os
my_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(my_dir, '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from unittest import TestCase

from google.appengine.ext import ndb, testbed
from google.appengine.datastore import datastore_stub_util


SAMPLE_AUTHORS = (
    ('Bob', 'Boston'),
    ('Harry', 'Houston'),
    ('Linda', 'London'),
)


class DummyPostData(dict):
    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v


def fill_authors(Author):
    """
    Fill authors from SAMPLE_AUTHORS.
    Model is passed so it can be either an NDB or DB model.
    """
    AGE_BASE = 30
    authors = []
    for name, city in SAMPLE_AUTHORS:
        author = Author(name=name, city=city, age=AGE_BASE)
        author.put()
        authors.append(author)
        AGE_BASE += 1
    return authors


class NDBTestCase(TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()

        policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(
            probability=1)
        self.testbed.init_datastore_v3_stub(consistency_policy=policy)

        ctx = ndb.get_context()
        ctx.set_cache_policy(False)
        ctx.set_memcache_policy(False)

    def tearDown(self):
        self.testbed.deactivate()



class DBTestCase(TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()

        policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(
            probability=1)
        self.testbed.init_datastore_v3_stub(consistency_policy=policy)

    def tearDown(self):
        self.testbed.deactivate()
