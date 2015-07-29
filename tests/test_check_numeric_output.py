from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


from check_numeric_output import CheckNumericOutput
from naglib.nagiosplugin import NAG_OK, NAG_CRITICAL, NAG_WARNING, NAG_MESSAGES


__author__ = 'jaclu'

class PortalRevTestCase(TestCase):
    def test_no_param(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        f = open(os.devnull, 'w')
        try:
            _stdout = sys.stdout
            sys.stdout = f
            code, msg = CheckNumericOutput().run()
        except SystemExit as e:
            sys.stdout = _stdout
            self.assertEqual(e.message, 0, 'no params should use exit code 0')
            return  # this is strange, sometimes we end up here...
        sys.stdout = _stdout
        self.assertEqual(code, NAG_CRITICAL, 'no param should fail with NAG_CRITICAL' )
        self.assertEqual(msg.split(':')[0], lbl,'response should be labeled %s' % lbl)

    def test_help(self):
        f = open(os.devnull, 'w')
        try:
            _stdout = sys.stdout
            sys.stdout = f
            a = CheckNumericOutput(['-h']).run()
        except SystemExit as e:
            sys.stdout = _stdout
            self.assertEqual(e.message, 0, 'Help should use exit code 0')
        return

    def test_no_flags(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        f = open(os.devnull, 'w')
        try:
            _stdout = sys.stdout
            sys.stdout = f
            code, msg = CheckNumericOutput(['echo "2"']).run()
        except SystemExit as e:
            sys.stdout = _stdout
            self.assertEqual(e.message, 0, 'Help should use exit code 0')
        sys.stdout = _stdout
        self.assertEqual(code, NAG_CRITICAL, 'no flags should fail with NAG_CRITICAL' )
        self.assertEqual(msg.split(':')[0], lbl,'response should be labeled %s' % lbl)

    def test_low_warning(self):
        lbl = NAG_MESSAGES[NAG_WARNING]
        code, msg = CheckNumericOutput(['echo "2"', '-w 3']).run()
        self.assertEqual(code, NAG_WARNING,'to low warn value should fail with NAG_WARNING')
        self.assertEqual(msg.split(':')[0], lbl,'response should be labeled %s' % lbl)

    def test_high_warning(self):
        lbl = NAG_MESSAGES[NAG_WARNING]
        code, msg = CheckNumericOutput(['echo "2"', '-W 1']).run()
        self.assertEqual(code, NAG_WARNING,'to high warn value should fail with NAG_WARNING')
        self.assertEqual(msg.split(':')[0], lbl,'to high warn value should be labeled %s' % lbl)

    def test_low_critical(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckNumericOutput(['echo "2"', '-c 3']).run()
        self.assertEqual(code, NAG_CRITICAL,'to low crit value should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl,'response should be labeled %s' % lbl)

    def test_high_critical(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckNumericOutput(['echo "2"', '-C 1']).run()
        self.assertEqual(code, NAG_CRITICAL,'to high crit value should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl,'response should be labeled %s' % lbl)

    def test_high_critical_multi_param(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckNumericOutput(['echo "25"', '-w 3', '-c 1', '-W 10', '-C 20']).run()
        self.assertEqual(code, NAG_CRITICAL,'to high crit value should fail with NAG_CRITICAL')
        self.assertEqual(msg.split(':')[0], lbl,'response should be labeled %s' % lbl)

    def test_low_warn_equals_low_crit(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckNumericOutput(['echo "25"', '-w 10', '-c 10']).run()
        self.assertEqual(code, NAG_CRITICAL, msg)
        self.assertEqual(msg.split(':')[0], lbl,'response should be labeled %s' % lbl)

    def test_low_warn_smaler_than_low_crit(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckNumericOutput(['echo "25"', '-w 8', '-c 10']).run()
        self.assertEqual(code, NAG_CRITICAL, msg)
        self.assertEqual(msg.split(':')[0], lbl,'response should be labeled %s' % lbl)

    def test_high_crit_equals_high_warn(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckNumericOutput(['echo "25"', '-W 10', '-C 10']).run()
        self.assertEqual(code, NAG_CRITICAL, msg)
        self.assertEqual(msg.split(':')[0], lbl,'response should be labeled %s' % lbl)

    def test_high_crit_lower_than_high_warn(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckNumericOutput(['echo "25"', '-W 12', '-C 10']).run()
        self.assertEqual(code, NAG_CRITICAL, msg)
        self.assertEqual(msg.split(':')[0], lbl,'response should be labeled %s' % lbl)



