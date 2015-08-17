__author__ = 'jaclu'

from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.tests.stdout_redirector import Capturing
from src.naglib import NAG_MESSAGES, NAG_OK, NAG_WARNING, NAG_CRITICAL
from src.check_file_exists import CheckFileExists


MISSING_FILE = '/not/likely/this/exists'
OK_FILE = '/etc/hosts'

class TestFileExists(TestCase):

    def test_no_param(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckFileExists().run()
        self.assertEqual(code, NAG_CRITICAL, 'no param should fail with %s' % lbl)
        self.assertEqual(msg, 'CRIT: Exactly one filename must be supplied as param', 'Bad no param message')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_help(self):
        lbl = NAG_MESSAGES[NAG_OK]
        try:
            with Capturing() as output:
                code, msg = CheckFileExists(['-h']).run()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK, 'Help should use exit code %s' % lbl)
        self.assertEqual(output.stdout_str().split(':')[0], 'Usage', 'Help should be displayed')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_file_found(self):
        lbl = NAG_MESSAGES[NAG_OK]
        with Capturing() as output:
            code, msg = CheckFileExists([OK_FILE]).run()
        perf_data = float(msg.split('file age=')[1].split(';')[0])
        self.assertEqual(code, NAG_OK)
        self.assertEqual(msg.split(':')[0], lbl, 'file found should be labeled %s' % lbl)
        self.assertGreater(perf_data, 0, 'file age should be positive')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_file_missing(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckFileExists([MISSING_FILE]).run()
        self.assertEqual(code, NAG_CRITICAL, '%s should not exist' % MISSING_FILE)
        self.assertEqual(msg.split(':')[0], lbl, 'file not found should be labeled %s' % lbl)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_file_missing_warning(self):
        lbl = NAG_MESSAGES[NAG_WARNING]
        with Capturing() as output:
            code, msg = CheckFileExists([MISSING_FILE, '-w']).run()
        perf_data = float(msg.split('file age=')[1].split(';')[0])
        self.assertEqual(code, NAG_WARNING, '%s should not exist' % MISSING_FILE)
        self.assertEqual(msg.split(':')[0], lbl, 'file not found with -w param should be labeled %s' % lbl)
        self.assertEqual(perf_data, 0, 'age of missing file should be 0')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_file_missing_reverse(self):
        lbl = NAG_MESSAGES[NAG_OK]
        with Capturing() as output:
            code, msg = CheckFileExists([MISSING_FILE, '-r']).run()
        perf_data = float(msg.split('file age=')[1].split(';')[0])
        self.assertEqual(code, NAG_OK, '%s should not exist' % MISSING_FILE)
        self.assertEqual(msg.split(':')[0], lbl, 'file not found with -r param should be labeled %s' % lbl)
        self.assertEqual(perf_data, 0, 'age of missing file should be 0')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_file_found_reverse(self):
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        with Capturing() as output:
            code, msg = CheckFileExists([OK_FILE, '-r']).run()
        perf_data = float(msg.split('file age=')[1].split(';')[0])
        self.assertEqual(code, NAG_CRITICAL, '%s should not exist' % OK_FILE)
        self.assertEqual(msg.split(':')[0], lbl, 'file found with -r param should be labeled %s' % lbl)
        self.assertGreater(perf_data, 0, 'file age should be positive')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_file_found_reverse_warning(self):
        lbl = NAG_MESSAGES[NAG_WARNING]
        with Capturing() as output:
            code, msg = CheckFileExists([OK_FILE, '-r', '-w']).run()
        perf_data = float(msg.split('file age=')[1].split(';')[0])
        self.assertEqual(code, NAG_WARNING, '%s should not exist' % OK_FILE)
        self.assertEqual(msg.split(':')[0], lbl, 'file found with -r param should be labeled %s' % lbl)
        self.assertGreater(perf_data, 0, 'file age should be positive')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')
