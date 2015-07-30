__author__ = 'jaclu'

from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.stdout_redirector import Capturing
from naglib.nagiosplugin import NAG_OK, NAG_CRITICAL, NAG_MESSAGES

from alternate_http import CheckHttp


class AlternateHttp(TestCase):
    def test_bad_host(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckHttp(['-u http://not.www.google.com', '-r', 'doesnt matter']).run()
        self.assertEqual(code, NAG_CRITICAL, 'bad host should fail with NAG_CRITICAL')
        self.assertEqual(msg, 'CRIT: Connection error', 'expected output not found')

    def test_invalid_response_absent(self):
        lbl = NAG_MESSAGES[NAG_OK]
        code, msg = CheckHttp(['-u http://www.google.com', '-r', '<title>NotGoogle</title>', '-n']).run()
        self.assertEqual(code, NAG_OK, 'invalid response absent should exit with NAG_OK')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)

    def test_invalid_response_present(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckHttp(['-u http://www.google.com', '-r', '<title>Google</title>', '-n']).run()
        self.assertEqual(code, NAG_CRITICAL, 'invalid response should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)

    def test_bad_response(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckHttp(['-u http://www.google.com', '-r', '<title>Not Google</title>']).run()
        self.assertEqual(code, NAG_CRITICAL, 'bad response should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)

    def test_good_response(self):
        lbl = NAG_MESSAGES[NAG_OK]
        code, msg = CheckHttp(['-u', 'http://www.google.com', '-r', '<title>Google</title>']).run()
        self.assertEqual(code, NAG_OK, 'response found should exit with NAG_OK')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)

    def test_no_response(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckHttp(['-u http://www.google.com']).run()
        self.assertEqual(code, NAG_CRITICAL, 'no response should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)

    def test_no_param(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckHttp().run()
        self.assertEqual(code, NAG_CRITICAL, 'no param should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)

    def test_help(self):
        try:
            with Capturing() as output:
                a = CheckHttp(['-h']).run()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, 0, 'Help should use exit code 0')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')
        self.assertEqual(output.stdout_join().split(':')[0], 'Usage', 'stdout looks suspicious')

