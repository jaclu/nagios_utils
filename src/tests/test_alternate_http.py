__author__ = 'jaclu'

from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.stdout_redirector import Capturing
from naglib.nagiosplugin import NAG_MESSAGES, NAG_OK, NAG_CRITICAL

from alternate_http import CheckAlternateHttp


class TestAlternateHttp(TestCase):

    def test_no_param(self):
        with Capturing() as output:
            code, msg = CheckAlternateHttp().run()
        # print('==== code ============')
        # print(code)
        # print('===== msg ===========')
        # print(msg)
        # print('===== stdout ===========')
        # print(output.stdout())
        # print('===== stderr ===========')
        # print(output.stderr())
        # print('================')
        self.assertEqual(code, NAG_CRITICAL)
        self.assertEqual(msg, 'CRIT: No url specified', 'Bad no param message')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_help(self):
        try:
            with Capturing() as output:
                code, msg = CheckAlternateHttp(['-h']).run()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK)
        self.assertEqual(output.stdout_str().split(':')[0], 'Usage', 'Help should be displayed')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_missing_option_url(self):
        with Capturing() as output:
            code, msg = CheckAlternateHttp(['-r', 'doesnt matter']).run()
        self.assertEqual(code, NAG_CRITICAL)
        self.assertEqual(msg, 'CRIT: No url specified')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_missing_option_response(self):
        with Capturing() as output:
            code, msg = CheckAlternateHttp(['-u', 'http://www.google.com']).run()
        self.assertEqual(code, NAG_CRITICAL)
        self.assertEqual(msg, 'CRIT: No response specified')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_response_should_exist(self):
        lbl = NAG_MESSAGES[NAG_OK]
        with Capturing() as output:
            code, msg = CheckAlternateHttp(['-u', 'http://www.google.com' , '-r', '<title>Google</title>']).run()
        self.assertEqual(code, NAG_OK)
        self.assertEqual(msg.split(':')[0], lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout output')
        self.assertEqual(output.stderr(), [], 'there should be no stderr output')

    def test_bad_response(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckAlternateHttp(['-u', 'http://www.google.com', '-r', '<title>NotGoogle</title>']).run()
        self.assertEqual(code, NAG_CRITICAL)
        self.assertEqual(msg.split(':')[0], lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout output')
        self.assertEqual(output.stderr(), [], 'there should be no stderr output')

    def test_not_allowed_found(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckAlternateHttp(['-u', 'http://www.google.com' , '-r', '<title>Google</title>', '-n']).run()
        self.assertEqual(code, NAG_CRITICAL)
        self.assertEqual(msg.split(':')[0], lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout output')
        self.assertEqual(output.stderr(), [], 'there should be no stderr output')

    def test_not_allowed_not_found(self):
        lbl = NAG_MESSAGES[NAG_OK]
        with Capturing() as output:
            code, msg = CheckAlternateHttp(['-u', 'http://www.google.com' , '-r', '<title>NotGoogle</title>', '-n']).run()
        self.assertEqual(code, NAG_OK)
        self.assertEqual(msg.split(':')[0], lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout output')
        self.assertEqual(output.stderr(), [], 'there should be no stderr output')

