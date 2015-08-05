from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


from check_portal_rev import CheckPortalRev
from naglib.nagiosplugin import NAG_MESSAGES, NAG_OK, NAG_CRITICAL, NAG_WARNING
from tests.stdout_redirector import Capturing
__author__ = 'jaclu'


K_HOST = 'host'
K_BRANCH = 'branch'
K_BUILD = 'build'
K_REV = 'rev'
K_VERS = 'vers'


class TestCheckPortalRev(TestCase):
    def __init__(self, *args, **argv):
        super(TestCheckPortalRev, self).__init__(*args, **argv)
        self._defaults = None
        self._ref_values = None

    def setUp(self):
        if not self._ref_values:
            self.runOnce()

    def runOnce(self):
        self._ref_values = {K_HOST: 'www.europeana.eu'}
        pr = CheckPortalRev([self._ref_values[K_HOST]])
        self._defaults = pr.options
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
            self._ref_values[key] = value


    def test_no_param(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckPortalRev().run()
        self.assertEqual(code, NAG_CRITICAL, 'no param should fail with %s' % lbl)
        self.assertEqual(msg, 'CRIT: This command must have exactly 1 arguments', 'Bad no param message')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_help(self):
        lbl = NAG_MESSAGES[NAG_OK]
        try:
            with Capturing() as output:
                code, msg = CheckPortalRev(['-h']).run()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK, 'Help should use exit code %s' % lbl)
        self.assertEqual(output.stdout_str().split(':')[0], 'Usage', 'Help should be displayed')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_host_good(self):
        lbl = NAG_MESSAGES[NAG_OK]
        with Capturing() as output:
            code, msg = CheckPortalRev([self._ref_values[K_HOST]]).run()
        self.assertEqual(code, NAG_OK, 'A valid host should display revision data')
        self.assertEqual(msg.split(':')[0], lbl, 'host found should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_host_bad(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckPortalRev(['www.google.com']).run()
        self.assertEqual(code, NAG_CRITICAL, 'On an invalid host, lack of revision data should be detected')
        self.assertEqual(msg.split(':')[0], lbl, 'invalid host should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_rev_good(self):
        lbl = NAG_MESSAGES[NAG_OK]
        with Capturing() as output:
            code, msg = CheckPortalRev([self._ref_values[K_HOST], '-r', self._ref_values[K_REV]]).run()
        self.assertEqual(code, NAG_OK, 'correct revision should not fail')
        self.assertEqual(msg.split(':')[0], lbl, 'correct revision should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_rev_bad(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckPortalRev([self._ref_values[K_HOST], '-r', 'NOWAY']).run()
        self.assertEqual(code, NAG_CRITICAL, 'revision NOWAY should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'revision NOWAY should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_version_good(self):
        with Capturing() as output:
            code, msg = CheckPortalRev([self._ref_values[K_HOST], '-V', self._ref_values[K_VERS]]).run()
        self.assertEqual(code, NAG_OK, 'correct revision should not fail')
        self.assertEqual(msg.split(':')[0], 'OK',  'correct revision should be labeled OK')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_version_bad(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckPortalRev([self._ref_values[K_HOST], '-V', 'NOWAY']).run()
        self.assertEqual(code, NAG_CRITICAL, 'version NOWAY should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'version NOWAY should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_build_time_good(self):
        with Capturing() as output:
            code, msg = CheckPortalRev([self._ref_values[K_HOST], '-b', self._ref_values[K_BUILD]]).run()
        self.assertEqual(code, NAG_OK, 'correct buildtime should not fail')
        self.assertEqual(msg.split(':')[0], 'OK', 'correct buildtime should be labeled OK')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_build_time_bad(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckPortalRev([self._ref_values[K_HOST], '-b', '42']).run()
        self.assertEqual(code, NAG_CRITICAL, 'buildtime 42 should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'buildtime 42 should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_url_good(self):
        with Capturing() as output:
            code, msg = CheckPortalRev([self._ref_values[K_HOST], '-u', self._defaults.url]).run()
        self.assertEqual(code, NAG_OK, 'correct url should not fail')
        self.assertEqual(msg.split(':')[0], 'OK', 'correct url should be labeled OK')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_url_bad(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckPortalRev([self._ref_values[K_HOST], '-u', '/not/here']).run()
        self.assertEqual(code, NAG_CRITICAL, 'bad url should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'bad url should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')
