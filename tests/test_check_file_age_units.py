__author__ = 'jaclu'

from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.stdout_redirector import Capturing
from naglib.nagiosplugin import NAG_MESSAGES, NAG_OK, NAG_WARNING, NAG_CRITICAL
from check_file_age_units import CheckFileAgeUnits

good_file = '/etc/hosts'
bad_file = '/should/not/exist'


class TestFileAgeUnits(TestCase):

    def test_no_param(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        msg = None
        with Capturing() as output:
            code, msg = CheckFileAgeUnits().run()
        self.assertEqual(code, NAG_CRITICAL, 'no param should fail with %s' % lbl)
        self.assertEqual(msg, 'CRIT: This command must have exactly 1 arguments', 'Bad no param message')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_help(self):
        lbl = NAG_MESSAGES[NAG_OK]
        try:
            with Capturing() as output:
                code, msg = CheckFileAgeUnits(['-h']).run()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK, 'Help should use exit code %s' % lbl)
        self.assertEqual(output.stdout_str().split(':')[0], 'Usage', 'Help should be displayed')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_not_existing_file(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits([bad_file, '-w 1s', '-c 10s']).run()
        self.assertEqual(code, NAG_CRITICAL)
        self.assertEqual(msg, '%s: File not found: %s' % (NAG_MESSAGES[NAG_CRITICAL], bad_file))
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_not_existing_file_warn(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits([bad_file, '--warn-on-missing', '-w 1s', '-c 10s']).run()
        self.assertEqual(code, NAG_WARNING)
        self.assertEqual(msg, '%s: File not found: %s' % (NAG_MESSAGES[NAG_WARNING], bad_file))
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_existing_file_high_crit(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits([good_file, '-c 10000w']).run()
        self.assertEqual(code, NAG_OK, 'no way that file is 200 years old...')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_existing_file_low_warn_high_crit(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits([good_file, '-w 1s', '-c 10000w']).run()
        self.assertEqual(code, NAG_WARNING, 'no way that file is 200 years old...')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_existing_file_high_warn_higher_crit(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits([good_file, '-w 1000w', '-c 10000w']).run()
        self.assertEqual(code, NAG_OK, 'no way that file is 20 years old...')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_existing_file_low_crit(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits([good_file, '-c 1s']).run()
        self.assertEqual(code, NAG_CRITICAL, 'it should be older than one second...')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_existing_file_size_ok(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits([good_file, '--size-min', '1']).run()
        self.assertEqual(code, NAG_OK, 'it should be larger than one byte...')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_existing_file_size_small(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits([good_file, '--size-min', '100000000']).run()
        self.assertEqual(code, NAG_CRITICAL, 'it should be smaller than 100MB...')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_existing_file_size_large(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits([good_file, '--size-max', '1']).run()
        self.assertEqual(code, NAG_CRITICAL, 'it should be smaller than 100MB...')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_existing_file_size_min_larger_than_max(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits([good_file, '--size-min', '10', '--size-max', '1']).run()
        self.assertEqual(code, NAG_CRITICAL, 'min > max should trigger error')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_existing_file_size_exact(self):
        size = str(os.path.getsize(good_file))
        with Capturing() as output:
            code, msg = CheckFileAgeUnits([good_file, '--size-min', size, '--size-max', size]).run()
        self.assertEqual(code, NAG_OK, 'exact size should be accepted')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_existing_file_size_exact_but_too_old(self):
        size = str(os.path.getsize(good_file))
        with Capturing() as output:
            code, msg = CheckFileAgeUnits([good_file, '--size-min', size, '--size-max', size, '-c 1s']).run()
        self.assertEqual(code, NAG_CRITICAL, 'it should be older than one second...')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_in_dir_oldest(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits(['/etc', '--oldest', '-c 10000w']).run()
        self.assertEqual(code, NAG_OK, "oldest file shouldn't be 200 years")
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_in_dir_youngest(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits(['/etc', '--newest', '-c 10000w']).run()
        self.assertEqual(code, NAG_OK, "youngest file shouldn't be 200 years")
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_in_dir_youngest_and_oldest(self):
        with Capturing() as output:
            code, msg = CheckFileAgeUnits(['/etc',  '--newest', '--oldest', '-c 10000w']).run()
        self.assertEqual(code, NAG_CRITICAL, "--newest abd --oldest can't be combined")
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

