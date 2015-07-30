__author__ = 'jaclu'

from unittest import TestCase


# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.stdout_redirector import Capturing
from naglib.nagiosplugin import _perf_value, NagiosPlugin, NAG_MESSAGES, NAG_OK


class NagiosPluginPerfValue(TestCase):
    def test_perf_value_flot(self):
        self.assertEqual(_perf_value(1.2), '1.20', 'ensuring one digit is rounded to two digits')
        self.assertEqual(_perf_value(1.2345), '1.23', 'ensuring many digits are rounded to two digits')

    def test_perf_valuue_int(self):
        self.assertEqual(_perf_value(1), '1.00', 'ensuring one digit is rounded to two digits')

    def test_perf_value_str(self):
        perf = _perf_value('foo')
        self.assertEqual(perf, '', 'String params should return empty')


dummy_cmd = '/not/likely/this/exists'
ok_output = '%s: %s' % (NAG_MESSAGES[NAG_OK], dummy_cmd)


class TestNagiosPlugin(NagiosPlugin):
    def workload(self):
        return self.exit_ok(dummy_cmd)


class NagiospluginNagiosPlugin(TestCase):
    def test_nagiosplugin_show_options(self):
        with Capturing() as output:
            TestNagiosPlugin(['-v']).show_options()
        self.assertEqual(output.stdout(),
                         ['Options for program (* indicates default)', '  nsca = * ', '  verbose = 1 '],
                         'Expected output from show_options() not found')
        self.assertEqual(output.stderr(), [], 'there should be no stderr')

    def test_run_sandalone_false(self):
        code, msg = TestNagiosPlugin().run()
        self.assertEqual(code, 0, 'dummy cmd should exit 0')
        self.assertEqual(msg, ok_output, 'output should be dummy cmd')

    def test_run_sandalone_true(self):
        try:
            with Capturing() as output:
                TestNagiosPlugin().run(standalone=True)
        except SystemExit as e:
            code = e.args[0]
        self.assertEqual(code, 0, 'dummy cmd should exit 0')
        self.assertEqual(output.stdout(), [ok_output], 'output should be dummy cmd')
        self.assertEqual(output.stderr(), [], 'there should be no stderr output')

    def test_run_ignore_verbose(self):
        with Capturing() as output:
            code, msg = TestNagiosPlugin(['-v', '-v', '-v']).run(ignore_verbose=False)

        self.assertEqual(code, 0, 'dummy cmd should exit 0')
        self.assertEqual(msg, ok_output, 'output should be dummy cmd')
        self.assertEqual(output.stdout_join().find('Options for program'), 0, 'stdout looks suspicious')
        self.assertEqual(output.stderr(), [], 'there should be no stderr output')
