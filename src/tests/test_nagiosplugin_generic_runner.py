__author__ = 'jaclu'

from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.tests.stdout_redirector import Capturing
from src.naglib import GenericRunner, NAG_MESSAGES, NAG_OK, NAG_CRITICAL, NAG_WARNING


class TestNagiospluginGenericRunner(TestCase):

    def test_constructor(self):
        code = None
        try:
            with Capturing() as output:
                GenericRunner()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, None, 'Constructor shouldnt fail')
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_help(self):
        try:
            with Capturing() as output:
                code, msg = GenericRunner(['-h']).run()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK)
        self.assertEqual(output.stdout_str().split(':')[0], 'Usage', 'Help should be displayed')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_log_lvl_0(self):
        msg = 'foo'
        gr = GenericRunner()
        with Capturing() as output:
            gr.log(msg)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_log_lvl_0_forced_msg(self):
        msg = 'foo'
        gr = GenericRunner()
        with Capturing() as output:
            gr.log(msg, 0)
        self.assertEqual(output.stdout(), [msg], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_log_lvl_1(self):
        msg = 'foo'
        gr = GenericRunner(['-v'])
        with Capturing() as output:
            gr.log(msg)
        self.assertEqual(output.stdout(), [msg], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_log_lvl_1_lvl2_msg(self):
        msg = 'foo'
        gr = GenericRunner(['-v'])
        with Capturing() as output:
            gr.log(msg, 2)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')


    def test_bad_param(self):
        code = 'not triggered'
        bad_param = '--holka'
        try:
            with Capturing() as output:
                GenericRunner([bad_param])
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_CRITICAL)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr()[-1].split('error: ')[1], 'no such option: %s' % bad_param,
                         'Ensurr last line to stderr is an error mentioning the bad param')

    def test_empty_workload(self):
        code = 'not triggered'
        gr = GenericRunner()
        try:
            with Capturing() as output:
                gr.workload()  # also uses exit_crit()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_CRITICAL, 'workload() should terminate with NAG_CRITICAL)')
        self.assertEqual(output.stdout(), ['CRIT: Plugin implementation must define a workload()!'],
                         'Printed error msg doesnt match expectation')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_url_get(self):
        html = GenericRunner().url_get('http://www.google.com')
        b = html.find('<title>Google</title>') > -1
        self.assertTrue(b, 'Google should be in text')

    def test_exit_ok(self):
        expected_code = NAG_OK
        code = 'not triggered'
        msg = 'sample text'
        try:
            with Capturing() as output:
                GenericRunner().exit_ok(msg)
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, expected_code)
        self.assertEqual(output.stdout(), ['%s: %s' % (NAG_MESSAGES[expected_code], msg)])

    def test_exit_warn(self):
        expected_code = NAG_WARNING
        code = 'not triggered'
        msg = 'sample text'
        try:
            with Capturing() as output:
                GenericRunner().exit_warn(msg)
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, expected_code)
        self.assertEqual(output.stdout(), ['%s: %s' % (NAG_MESSAGES[expected_code], msg)])

    def test_exit_crit(self):
        expected_code = NAG_CRITICAL
        code = 'not triggered'
        msg = 'sample text'
        try:
            with Capturing() as output:
                GenericRunner().exit_crit(msg)
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, expected_code)
        self.assertEqual(output.stdout(), ['%s: %s' % (NAG_MESSAGES[expected_code], msg)])
