from unittest import TestCase

from google.appengine.ext import ndb, testbed
from google.appengine.datastore import datastore_stub_util


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


