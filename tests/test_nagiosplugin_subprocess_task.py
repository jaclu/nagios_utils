__author__ = 'jaclu'

from unittest import TestCase
from tests.stdout_redirector import Capturing

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from naglib.nagiosplugin import SubProcessTask, NAG_CRITICAL

dummy_cmd = '/not/likely/this/exists'


class NagiospluginSubProcess(TestCase):
    def test_cmd_execute_output(self):
        self.assertEqual(SubProcessTask().cmd_execute_output('true'), (0, '', ''), 'true should succeed with no output')
        code, stdout, stderr = SubProcessTask().cmd_execute_output(dummy_cmd)
        self.assertEqual(code, 127, 'cmd not found should exit 127')

    def test_cmd_execute1(self):
        self.assertEqual(SubProcessTask().cmd_execute1('true'), 0, 'true should exit 0')
        msg = SubProcessTask().cmd_execute1(dummy_cmd)
        self.assertEqual(msg, 'retcode: 127\nstderr: /bin/sh: /not/likely/this/exists: No such file or directory\n',
                         'expected output not found')

    def test_cmd_execute_raise_on_error_no_error(self):
        self.assertTrue(SubProcessTask().cmd_execute_raise_on_error('true'), 'good cmd should exit True')

    def test_cmd_execute_raise_on_error_is_error(self):
        b = False
        try:
            SubProcessTask().cmd_execute_raise_on_error(dummy_cmd)
        except Exception:
            b = True
        self.assertTrue(b, 'bad cmd should fail')

    def test_cmd_execute_abort_on_error(self):
        self.assertEqual(SubProcessTask().cmd_execute_abort_on_error('true'), '', 'good cmd')
        code = 'not triggered'
        try:
            with Capturing() as output:
                SubProcessTask().cmd_execute_abort_on_error(dummy_cmd)
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, NAG_CRITICAL, 'bad cmd should fail')
        self.assertEqual(output.stdout(),
                         ['CRIT: Errormsg: /bin/sh: /not/likely/this/exists: No such file or directory', ''],
                         'Expected output from cmd_execute_abort_on_error() not found')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')
