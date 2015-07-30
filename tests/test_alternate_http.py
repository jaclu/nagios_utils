__author__ = 'jaclu'

from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from naglib.nagiosplugin import NAG_OK, NAG_CRITICAL, NAG_MESSAGES

from alternate_http import CheckHttp


class AlternateHttpTestCase(TestCase):
    def test_bad_host(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckHttp(['-u http://not.www.google.com', '-r', 'doesnt matter']).run()
        self.assertEqual(code, NAG_CRITICAL, 'bad host should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)

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
        f = open(os.devnull, 'w')
        _stdout = sys.stdout
        sys.stdout = f
        code, msg = CheckHttp(['-u http://www.google.com']).run()
        sys.stdout = _stdout
        self.assertEqual(code, NAG_CRITICAL, 'no response should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)

    def test_no_param(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        f = open(os.devnull, 'w')
        _stdout = sys.stdout
        try:
            sys.stdout = f
            code, msg = CheckHttp().run()
        except SystemExit as e:
            sys.stdout = _stdout
            self.assertEqual(e.args[0], NAG_CRITICAL, 'no params should fail with NAG_CRITICAL')
            return  # this is strange, sometimes we end up here...
        sys.stdout = _stdout
        self.assertEqual(code, NAG_CRITICAL, 'no param should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)

    def test_help(self):
        f = open(os.devnull, 'w')
        _stdout = sys.stdout
        try:
            sys.stdout = f
            a = CheckHttp(['-h']).run()
        except SystemExit as e:
            sys.stdout = _stdout
            self.assertEqual(e.args[0], 0, 'Help should use exit code 0')
        return

