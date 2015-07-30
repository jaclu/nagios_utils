__author__ = 'jaclu'

from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from naglib.nagiosplugin import NAG_MESSAGES, NAG_OK, NAG_WARNING, NAG_CRITICAL
from check_file_exists import CheckFileExists



class FileExistsTestBase(TestCase):

    def test_help(self):
        f = open(os.devnull, 'w')
        _stdout = sys.stdout
        try:
            sys.stdout = f
            a = CheckFileExists(['-h']).run()
        except SystemExit as e:
            sys.stdout = _stdout
            self.assertEqual(e.args[0], 0, 'Help should use exit code 0')
        return

    def test_file_found(self):
        fn = '/etc/hosts'
        lbl = NAG_MESSAGES[NAG_OK]
        code, msg = CheckFileExists([fn]).run()
        perf_data = float(msg.split('file age=')[1].split(';')[0])
        self.assertEqual(code, NAG_OK, '%s should exist' % fn)
        self.assertEqual(msg.split(':')[0], lbl, 'file found should be labeled %s' % lbl)
        self.assertGreater(perf_data, 0, 'file age should be positive')
        print (perf_data)

    def test_file_missing(self):
        fn = '/file/should/not/exist'
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckFileExists([fn]).run()
        perf_data = float(msg.split('file age=')[1].split(';')[0])
        self.assertEqual(code, NAG_CRITICAL, '%s should not exist' % fn)
        self.assertEqual(msg.split(':')[0], lbl, 'file not found should be labeled %s' % lbl)
        self.assertEqual(perf_data, 0, 'age of missing file should be 0')

    def test_file_missing_warning(self):
        fn = '/file/should/not/exist'
        lbl = NAG_MESSAGES[NAG_WARNING]
        code, msg = CheckFileExists([fn, '-w']).run()
        perf_data = float(msg.split('file age=')[1].split(';')[0])
        self.assertEqual(code, NAG_WARNING, '%s should not exist' % fn)
        self.assertEqual(msg.split(':')[0], lbl, 'file not found with -w param should be labeled %s' % lbl)
        self.assertEqual(perf_data, 0, 'age of missing file should be 0')

    def test_file_missing_reverse(self):
        fn = '/file/should/not/exist'
        lbl = NAG_MESSAGES[NAG_OK]
        code, msg = CheckFileExists([fn, '-r']).run()
        perf_data = float(msg.split('file age=')[1].split(';')[0])
        self.assertEqual(code, NAG_OK, '%s should not exist' % fn)
        self.assertEqual(msg.split(':')[0], lbl, 'file not found with -r param should be labeled %s' % lbl)
        self.assertEqual(perf_data, 0, 'age of missing file should be 0')

    def test_file_found_reverse(self):
        fn = '/etc/hosts'
        lbl = NAG_MESSAGES[NAG_CRITICAL]
        code, msg = CheckFileExists([fn, '-r']).run()
        perf_data = float(msg.split('file age=')[1].split(';')[0])
        self.assertEqual(code, NAG_CRITICAL, '%s should not exist' % fn)
        self.assertEqual(msg.split(':')[0], lbl, 'file found with -r param should be labeled %s' % lbl)
        self.assertGreater(perf_data, 0, 'file age should be positive')

    def test_file_found_reverse_warning(self):
        fn = '/etc/hosts'
        lbl = NAG_MESSAGES[NAG_WARNING]
        code, msg = CheckFileExists([fn, '-r', '-w']).run()
        perf_data = float(msg.split('file age=')[1].split(';')[0])
        self.assertEqual(code, NAG_WARNING, '%s should not exist' % fn)
        self.assertEqual(msg.split(':')[0], lbl, 'file found with -r param should be labeled %s' % lbl)
        self.assertGreater(perf_data, 0, 'file age should be positive')
