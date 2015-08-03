__author__ = 'jaclu'

from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from check_numeric_output import CheckNumericOutput
from naglib.nagiosplugin import NAG_MESSAGES, NAG_OK, NAG_CRITICAL, NAG_WARNING
from tests.stdout_redirector import Capturing
from check_http_size import CheckHttpSize

class TestCheckHttpSize(TestCase):

    def test_no_param(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckHttpSize().run()
        self.assertEqual(code, NAG_CRITICAL, 'no param should fail with %s' % lbl)
        self.assertEqual(msg, 'CRIT: Mandatory param missing')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_help(self):
        lbl = NAG_MESSAGES[NAG_OK]
        try:
            with Capturing() as output:
                code, msg = CheckHttpSize(['-h']).run()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK, 'Help should use exit code %s' % lbl)
        self.assertEqual(output.stdout_str().split(':')[0], 'Usage', 'Help should be displayed')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_larger_than_min(self):
        with Capturing() as output:
            code, msg = CheckHttpSize(['http://www.sunet.se', '-w 1:']).run()
        self.assertEqual(code, NAG_OK, "This shouldn't fail")
