__author__ = 'jaclu'

from unittest import TestCase


# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.naglib import _perf_value




class NagiosPluginPerfValue(TestCase):
    def test_perf_value_flot(self):
        self.assertEqual(_perf_value(1.2), '1.20', 'ensuring one digit is rounded to two digits')
        self.assertEqual(_perf_value(1.2345), '1.23', 'ensuring many digits are rounded to two digits')

    def test_perf_valuue_int(self):
        self.assertEqual(_perf_value(2), '2.00', 'ensuring one digit is rounded to two digits')

    def test_perf_valuue_int_zero(self):
        self.assertEqual(_perf_value(0), '0.00', 'ensuring one digit is rounded to two digits')

    def test_perf_value_str(self):
        perf = _perf_value('foo')
        self.assertEqual(perf, '', 'String params should return empty')

    def test_perf_value_None(self):
        perf = _perf_value(None)
        self.assertEqual(perf, '', 'String params should return empty')
