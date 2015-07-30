__author__ = 'jaclu'

from unittest import TestCase

# make sure dir above is in search path for pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from naglib.nagiosplugin import GenericRunner, NAG_WARNING, NAG_CRITICAL, NAG_OK

class NagiospluginGenericRunnerTestCase(TestCase):
    def test_help(self):
        b = False
        f = open(os.devnull, 'w')
        _stdout = sys.stdout
        sys.stdout = f
        try:
            a = GenericRunner(['-h'])
        except SystemExit as e:
            if e.args[0] == 0:
                b = True
        sys.stdout = _stdout
        self.assertTrue(b, 'Help should terminate with SystemExit(0)')

    def test_bad_param(self):
        code = 'not triggered'
        f = open(os.devnull, 'w')
        _stderr = sys.stderr
        sys.stderr = f
        try:
            a = GenericRunner(['--holka'])
        except SystemExit as e:
            code = e.args[0]
        sys.stderr = _stderr
        self.assertEqual(code, 2, 'Bad param should terminate with SystemExit(2)')

    def test_workload(self):
        code = 'not triggered'
        f = open(os.devnull, 'w')
        _stdout = sys.stdout
        gr = GenericRunner()
        sys.stdout = f
        try:
            gr.workload()  # also uses exit_crit()
        except SystemExit as e:
            code = e.args[0]
        sys.stdout = _stdout
        self.assertEqual(code, NAG_CRITICAL, 'workload() should terminate with NAG_CRITICAL)')

    def test_exit_help(self):
        code = 'not triggered'
        f = open(os.devnull, 'w')
        _stdout = sys.stdout
        gr = GenericRunner(['-q'])
        sys.stdout = f
        try:
            gr.exit_help('help me')
        except SystemExit as e:
            code = e.args[0]
        sys.stdout = _stdout
        self.assertEqual(code, 2, 'exit_help() param should terminate with SystemExit(2)')

    def test_url_get(self):
        html = GenericRunner().url_get('http://www.google.com')
        b = html.find('<title>Google</title>') > -1
        self.assertTrue(b,'Google should be in text')

    def test_exit_warn(self):
        code = 'not triggered'
        f = open(os.devnull, 'w')
        _stdout = sys.stdout
        sys.stdout = f
        try:
            s = GenericRunner().exit_warn('warn msg')
        except SystemExit as e:
            code = e.args[0]
        sys.stdout = _stdout
        self.assertEqual(code, NAG_WARNING, 'exit_warn() should terminate with NAG_WARNING')

    def test_exit_ok(self):
        code = 'not triggered'
        f = open(os.devnull, 'w')
        _stdout = sys.stdout
        sys.stdout = f
        try:
            s = GenericRunner().exit_ok('ok msg')
        except SystemExit as e:
            code = e.args[0]
        sys.stdout = _stdout
        self.assertEqual(code, NAG_OK, 'exit_ok() should terminate with NAG_OK')
