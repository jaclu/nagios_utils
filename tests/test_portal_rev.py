from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


from check_portal_rev import PortalRev
from naglib.nagiosplugin import NAG_OK, NAG_CRITICAL, NAG_MESSAGES
from tests.stdout_redirector import Capturing
__author__ = 'jaclu'


K_HOST = 'host'
K_BRANCH = 'branch'
K_BUILD = 'build'
K_REV = 'rev'
K_VERS = 'vers'

DEFAULTS = REF_VALUES = None


class PortalRevTestBase(TestCase):
    def setUp(self):
        if not DEFAULTS:
            self.runOnce()

    def runOnce(self):
        global DEFAULTS
        global REF_VALUES

        REF_VALUES = {K_HOST: 'www.europeana.eu'}
        pr = PortalRev([REF_VALUES[K_HOST]])
        DEFAULTS = pr.options
        code, msg = pr.run()
        self.assertEqual(code, NAG_OK, 'Failed to find example params!')
        self.assertEqual(msg.split(':')[0], 'OK', 'Test did not result with OK!')
        for part in msg.split():
            parts2 = part.split(':')
            key = parts2[0]
            if key == 'OK':
                continue  # special case don't store this one
            self.assertIn(key, (K_HOST, K_BRANCH, K_BUILD, K_REV, K_VERS), 'Invalid key field: %s' % key)
            value = ':'.join(parts2[1:])
            REF_VALUES[key] = value


class TestPortalRev(PortalRevTestBase):

    def test_help(self):
        try:
            with Capturing() as output:
                PortalRev(['-h']).run()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK, 'Help should use exit code 0')
        self.assertEqual(output.stdout_join().split(':')[0], 'Usage', 'Help should be displayed')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_host_good(self):
        lbl = NAG_MESSAGES[NAG_OK]
        code, msg = PortalRev([REF_VALUES[K_HOST]]).run()
        self.assertEqual(code, NAG_OK, 'A valid host should display revision data')
        self.assertEqual(msg.split(':')[0], lbl, 'host found should be labeled %s' % lbl)

    def test_host_bad(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = PortalRev(['www.google.com']).run()
        self.assertEqual(code, NAG_CRITICAL, 'On an invalid host, lack of revision data should be detected')
        self.assertEqual(msg.split(':')[0], lbl, 'invalid host should be labeled %s' % lbl)

    def test_rev_good(self):
        lbl = NAG_MESSAGES[NAG_OK]
        code, msg = PortalRev([REF_VALUES[K_HOST], '-r', REF_VALUES[K_REV]]).run()
        self.assertEqual(code, NAG_OK, 'correct revision should not fail')
        self.assertEqual(msg.split(':')[0], lbl, 'correct revision should be labeled %s' % lbl)

    def test_rev_bad(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = PortalRev([REF_VALUES[K_HOST], '-r', 'NOWAY']).run()
        self.assertEqual(code, NAG_CRITICAL, 'revision NOWAY should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'revision NOWAY should be labeled %s' % lbl)

    def test_version_good(self):
        code, msg = PortalRev([REF_VALUES[K_HOST], '-V', REF_VALUES[K_VERS]]).run()
        self.assertEqual(code, NAG_OK, 'correct revision should not fail')
        self.assertEqual(msg.split(':')[0], 'OK',  'correct revision should be labeled OK')

    def test_version_bad(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = PortalRev([REF_VALUES[K_HOST], '-V', 'NOWAY']).run()
        self.assertEqual(code, NAG_CRITICAL, 'version NOWAY should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'version NOWAY should be labeled %s' % lbl)

    def test_build_time_good(self):
        code, msg = PortalRev([REF_VALUES[K_HOST], '-b', REF_VALUES[K_BUILD]]).run()
        self.assertEqual(code, NAG_OK, 'correct buildtime should not fail')
        self.assertEqual(msg.split(':')[0], 'OK', 'correct buildtime should be labeled OK')

    def test_build_time_bad(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = PortalRev([REF_VALUES[K_HOST], '-b', '42']).run()
        self.assertEqual(code, NAG_CRITICAL, 'buildtime 42 should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'buildtime 42 should be labeled %s' % lbl)

    def test_url_good(self):
        code, msg = PortalRev([REF_VALUES[K_HOST], '-u', DEFAULTS.url]).run()
        self.assertEqual(code, NAG_OK, 'correct url should not fail')
        self.assertEqual(msg.split(':')[0], 'OK', 'correct url should be labeled OK')

    def test_url_bad(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = PortalRev([REF_VALUES[K_HOST], '-u', '/not/here']).run()
        self.assertEqual(code, NAG_CRITICAL, 'bad url should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'bad url should be labeled %s' % lbl)

