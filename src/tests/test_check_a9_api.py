__author__ = 'jaclu'


from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.stdout_redirector import Capturing
from naglib.nagiosplugin import NAG_OK

from check_a9_api import CheckAny9Api

# TODO more tests needed
class TestCheckAny9Api(TestCase):
    def test_no_param(self):
        with Capturing() as output:
            code, msg = CheckAny9Api().run()
        print('e')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_help(self):
        try:
            with Capturing() as output:
                code, msg = CheckAny9Api(['-h']).run()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK)
        self.assertEqual(output.stdout_str().split(':')[0], 'Usage', 'Help should be displayed')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')


