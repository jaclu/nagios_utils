__author__ = 'jaclu'

from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from naglib.nagiosplugin import NAG_MESSAGES, NAG_OK, NAG_CRITICAL
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

    def test_min_value(self):
        with Capturing() as output:
            code, msg = CheckHttpSize(['http://www.sunet.se', '-w 1:']).run()
        self.assertEqual(code, NAG_OK)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_max_value(self):
        with Capturing() as output:
            code, msg = CheckHttpSize(['http://www.sunet.se', '-w :1000000']).run()
        self.assertEqual(code, NAG_OK)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_parse_size_span_param_none(self):
        hs = CheckHttpSize()
        try:
            with Capturing() as output:
                hs.parse_size_span(None,'hep')
        except SystemExit as e:
            error = e.args[0]
        self.assertEqual(error, NAG_CRITICAL)
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_parse_size_span_param_int(self):
        hs = CheckHttpSize()
        try:
            with Capturing() as output:
                hs.parse_size_span(None,'hep')
        except SystemExit as e:
            error = e.args[0]
        self.assertEqual(error, NAG_CRITICAL)
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_parse_size_span_one_value(self):
        hs = CheckHttpSize()
        with Capturing() as output:
            r = hs.parse_size_span('10','hep')
        self.assertEqual(r, (10, 10))
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_parse_size_span_two_values(self):
        hs = CheckHttpSize()
        with Capturing() as output:
            r = hs.parse_size_span('10:20','hep')
        self.assertEqual(r, (10, 20))
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_parse_size_span_three_values(self):
        error = None
        hs = CheckHttpSize()
        try:
            with Capturing() as output:
                hs.parse_size_span('10:20:30','hep')
        except SystemExit as e:
            error = e.args[0]
        self.assertEqual(error, NAG_CRITICAL)
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_parse_size_span_min_value(self):
        hs = CheckHttpSize()
        with Capturing() as output:
            r = hs.parse_size_span('10:','hep')
        self.assertEqual(r, (10, 99999999))
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_parse_size_span_max_value(self):
        hs = CheckHttpSize()
        with Capturing() as output:
            r = hs.parse_size_span(':10','hep')
        self.assertEqual(r, (-1, 10))
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_parse_size_span_decrease(self):
        hs = CheckHttpSize()
        try:
            with Capturing() as output:
                hs.parse_size_span('20:10','hep')
        except SystemExit as e:
            error = e.args[0]
        self.assertEqual(error, NAG_CRITICAL)
        self.assertEqual(output.stderr(), [], 'there should be no stderr')
