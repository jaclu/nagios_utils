__author__ = 'jaclu'

from unittest import TestCase


# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.tests.stdout_redirector import Capturing
from src.naglib import NagiosPlugin, NAG_MESSAGES, NAG_OK

dummy_result = 'Dummy command succeeded'
bad_cmd = '/not/likely/this/exists'
ok_output = '%s: %s' % (NAG_MESSAGES[NAG_OK], bad_cmd)


class DummytNagiosPlugin(NagiosPlugin):
    def workload(self):
        return self.exit_ok(dummy_result)


class TestNagiospluginNagiosPlugin(TestCase):

    def test_no_param(self):
        lbl = NAG_MESSAGES[NAG_OK]
        msg = None
        with Capturing() as output:
            code, msg = DummytNagiosPlugin().run()
        self.assertEqual(code, NAG_OK)
        self.assertEqual(msg, 'OK: %s' % dummy_result)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_help(self):
        try:
            with Capturing() as output:
                code, msg = DummytNagiosPlugin(['-h']).run()
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK)
        self.assertEqual(output.stdout()[0].split(':')[0], 'Usage', 'Help should be displayed')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_standalone(self):
        lbl = NAG_MESSAGES[NAG_OK]
        msg = None
        try:
            with Capturing() as output:
                DummytNagiosPlugin().run(standalone=True)
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK)
        self.assertEqual(output.stdout(), ['OK: %s' % dummy_result])
        self.assertEqual(output.stderr(), [], 'there should be no stderr')


    def test_nagiosplugin_show_options(self):
        with Capturing() as output:
            DummytNagiosPlugin(['-v']).show_options()
        self.assertEqual(output.stdout()[0].split('(')[0].strip(), 'Options for program')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_ignore_verbose(self):
        lbl = NAG_MESSAGES[NAG_OK]
        msg = None
        try:
            with Capturing() as output:
                code, msg = DummytNagiosPlugin(['-v', '-v', '-v']).run(ignore_verbose=True)
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_OK)
        self.assertEqual(msg, 'OK: %s' % dummy_result)
        self.assertEqual(output.stdout(), [], 'there should be no stdout')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')
