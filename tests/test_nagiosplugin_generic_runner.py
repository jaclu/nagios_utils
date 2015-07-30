__author__ = 'jaclu'

from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.stdout_redirector import Capturing
from naglib.nagiosplugin import GenericRunner, NAG_WARNING, NAG_CRITICAL, NAG_OK


class NagiospluginGenericRunner(TestCase):
    def test_help(self):
        b = False
        try:
            with Capturing():  # just filter output
                GenericRunner(['-h'])
        except SystemExit as e:
            if e.args[0] == 0:
                b = True
        self.assertTrue(b, 'Help should terminate with SystemExit(0)')

    def test_bad_param(self):
        code = 'not triggered'
        bad_param = '--holka'
        try:
            with Capturing() as output:
                GenericRunner([bad_param])
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, 2, 'Bad param should terminate with SystemExit(2)')
        self.assertEqual(output.stdout_join(), '', 'there should be no stdout')
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

    def test_exit_help(self):
        code = 'not triggered'
        gr = GenericRunner(['-q'])
        try:
            with Capturing() as output:
                gr.exit_help('help me')
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, 2, 'exit_help() param should terminate with SystemExit(2)')
        self.assertEqual(output.stdout()[-2:], ['*** help me', 'CRIT: bad param'],
                         'Stdout looks suspicious')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_url_get(self):
        html = GenericRunner().url_get('http://www.google.com')
        b = html.find('<title>Google</title>') > -1
        self.assertTrue(b, 'Google should be in text')

    def test_exit_warn(self):
        code = 'not triggered'
        msg = 'warn msg'
        try:
            with Capturing() as output:
                GenericRunner().exit_warn(msg)
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_WARNING, 'exit_warn() should terminate with NAG_WARNING')
        self.assertEqual(output.stdout_join(), 'WARN: %s' % msg, 'Ensuring expected output')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_exit_ok(self):
        code = 'not triggered'
        msg = 'ok msg'
        try:
            with Capturing() as output:
                GenericRunner().exit_ok(msg)
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK, 'exit_ok() should terminate with NAG_OK')
        self.assertEqual(output.stdout_join(), 'OK: %s' % msg, 'Ensuring expected output')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')
