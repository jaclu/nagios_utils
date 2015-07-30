__author__ = 'jaclu'

from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from naglib.nagiosplugin import GenericRunner, SubProcessTask, NAG_WARNING, NAG_CRITICAL, NAG_OK

dummy_cmd = '/not/likely/this/exists'

class NagiospluginSubProcessTaskTestCase(TestCase):
    def test_cmd_execute_output(self):
        self.assertEqual(SubProcessTask().cmd_execute_output('true'), (0,'',''), 'true should succeed with no output')
        code, stdout, stderr = SubProcessTask().cmd_execute_output(dummy_cmd)
        self.assertEqual(code, 127, 'cmd not found should exit 127')

    def test_cmd_execute1(self):
        self.assertEqual(SubProcessTask().cmd_execute1('true'), 0, 'true should exit 0')
        s = SubProcessTask().cmd_execute1(dummy_cmd)
        s2 = s.split('\n')[1].split()[0]
        self.assertEqual(s2,'stderr:', 'cmd not found should display "stderr:"')

    def test_cmd_execute_raise_on_error(self):
        self.assertTrue(SubProcessTask().cmd_execute_raise_on_error('true'),'good cmd should exit True')
        b = False
        try:
            a = SubProcessTask().cmd_execute_raise_on_error(dummy_cmd)
        except Exception as e:
            b = True
        self.assertTrue(b,'bad cmd should fail')

    def test_cmd_execute_abort_on_error(self):
        self.assertEqual(SubProcessTask().cmd_execute_abort_on_error('true'),'','good cmd')
        code = 'not triggered'
        f = open(os.devnull, 'w')
        _stdout = sys.stdout
        sys.stdout = f
        try:
            s = SubProcessTask().cmd_execute_abort_on_error(dummy_cmd)
        except SystemExit as e:
            code = e.args[0]
        sys.stdout = _stdout
        self.assertEqual(code, NAG_CRITICAL,'bad cmd should fail')
