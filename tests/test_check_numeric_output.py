from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from check_numeric_output import CheckNumericOutput
from naglib.nagiosplugin import NAG_MESSAGES, NAG_OK, NAG_CRITICAL, NAG_WARNING
from tests.stdout_redirector import Capturing


__author__ = 'jaclu'


class TestNumericOutput(TestCase):

    def test_no_param(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckNumericOutput().run()
        self.assertEqual(code, NAG_CRITICAL, 'no param should fail with %s' % lbl)
        self.assertEqual(msg, 'CRIT: You must specify a command to run (enclose with \'\' or "" if spaces are used)',
                         'Bad no param message')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_help(self):
        lbl = NAG_MESSAGES[NAG_OK]
        try:
            with Capturing() as output:
                code, msg = CheckNumericOutput(['-h']).run()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK, 'Help should use exit code %s' % lbl)
        self.assertEqual(output.stdout_str().split(':')[0], 'Usage', 'Help should be displayed')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_no_flags(self):
        with Capturing() as output:
            code, msg = CheckNumericOutput(['echo "2"']).run()
        self.assertEqual(code, NAG_CRITICAL, 'no flags should fail with NAG_CRITICAL')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_low_warning(self):
        lbl = NAG_MESSAGES[NAG_WARNING]
        with Capturing() as output:
            code, msg = CheckNumericOutput(['echo "2"', '-w 3']).run()
        self.assertEqual(code, NAG_WARNING, 'to low warn value should fail with NAG_WARNING')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_high_warning(self):
        lbl = NAG_MESSAGES[NAG_WARNING]
        with Capturing() as output:
            code, msg = CheckNumericOutput(['echo "2"', '-W 1']).run()
        self.assertEqual(code, NAG_WARNING, 'to high warn value should fail with NAG_WARNING')
        self.assertEqual(msg.split(':')[0], lbl, 'to high warn value should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_low_critical(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckNumericOutput(['echo "2"', '-c 3']).run()
        self.assertEqual(code, NAG_CRITICAL, 'to low crit value should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_high_critical(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckNumericOutput(['echo "2"', '-C 1']).run()
        self.assertEqual(code, NAG_CRITICAL, 'to high crit value should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_high_critical_multi_param(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckNumericOutput(['echo "25"', '-w 3', '-c 1', '-W 10', '-C 20']).run()
        self.assertEqual(code, NAG_CRITICAL, 'to high crit value should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_low_warn_equals_low_crit(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckNumericOutput(['echo "25"', '-w 10', '-c 10']).run()
        self.assertEqual(code, NAG_CRITICAL, msg)
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_low_warn_smaler_than_low_crit(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckNumericOutput(['echo "25"', '-w 8', '-c 10']).run()
        self.assertEqual(code, NAG_CRITICAL, msg)
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_high_crit_equals_high_warn(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckNumericOutput(['echo "25"', '-W 10', '-C 10']).run()
        self.assertEqual(code, NAG_CRITICAL, msg)
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_high_crit_lower_than_high_warn(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckNumericOutput(['echo "25"', '-W 12', '-C 10']).run()
        self.assertEqual(code, NAG_CRITICAL, msg)
        self.assertEqual(msg.split(':')[0], lbl, 'response should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')
