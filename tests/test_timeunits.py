__author__ = 'jaclu'

import time
from datetime import datetime
from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from naglib.timeunits import TimeUnits


class TimeunitsTestCase(TestCase):
    def test_eq_60s(self):
        self.assertEqual(TimeUnits(60), TimeUnits('60s'), '60 should be equal to 60s')

    def test_eq_1m(self):
        self.assertEqual(TimeUnits(60), TimeUnits('1m'), '60 should be equal to 1 minute')

    def test_eq_1h(self):
        self.assertEqual(TimeUnits(3600), TimeUnits('1h'), '3600 should be equal to 1 hour')

    def test_eq_1d(self):
        self.assertEqual(TimeUnits(3600 * 24), TimeUnits('1d'), '3600*24 should be equal to 1 day')

    def test_eq_1w(self):
        self.assertEqual(TimeUnits(3600 * 24 * 7), TimeUnits('1w'), '3600*24*7 should be equal to 1 week')

    def test_ne(self):
        self.assertNotEqual(TimeUnits(1), TimeUnits('2s'), '1s should be non equal to 2s')

    def test_lt(self):
        self.assertLess(TimeUnits(65), TimeUnits('66s'), '65s should be less than 66s')

    def test_le_less(self):
        self.assertLessEqual(TimeUnits(65), TimeUnits('66s'), '65s should be less or equal to 66s')

    def test_le_eqqual(self):
        self.assertLessEqual(TimeUnits(65), TimeUnits('65s'), '65s should be less or equal to 65s')

    def test_gt(self):
        self.assertGreater(TimeUnits(65), TimeUnits('64s'), '65s should be greater than 64s')

    def test_ge_greater(self):
        self.assertGreaterEqual(TimeUnits(65), TimeUnits('64s'), '65s should be greater or equal to 64s')

    def test_ge_equal(self):
        self.assertGreaterEqual(TimeUnits(65), TimeUnits('65s'), '65s should be greater or equal to 65s')

    def test_add(self):
        t1 = TimeUnits(65)
        t2 = TimeUnits('1m') + TimeUnits('5s')
        self.assertEqual(t1, t2, '65 should be equal to 1m + 5s')

    def test_delete(self):
        t1 = TimeUnits(55)
        t2 = TimeUnits('1m') - TimeUnits('5s')
        self.assertEqual(t1, t2, '55 should be equal to 1m - 5s')

    def test_datetime(self):
        dt = datetime.now()
        dt1 = TimeUnits(date_time=dt)
        time.sleep(1)
        dt2 = TimeUnits(date_time=dt)
        self.assertLess(dt1, dt2, 'Datetimes should be one sec apart')

    def test_bad_unit(self):
        try:
            TimeUnits('1q')
            raise AttributeError('1q should have triggered exception')
        except ValueError as e:
            self.assertEqual(e.args[0], 'Bad unit in param: 1q', 'Ensure correct msg for bad unit')

    def test_negative_time(self):
        with self.assertRaises(ValueError):
            TimeUnits(-1)

    def test_plural_params(self):
        with self.assertRaises(ValueError):
            TimeUnits('1m,2s')

    def test_non_numeric_input(self):
        with self.assertRaises(ValueError):
            TimeUnits('foo')

    def test_multiple_units(self):
        with self.assertRaises(ValueError):
            TimeUnits('1sw')

