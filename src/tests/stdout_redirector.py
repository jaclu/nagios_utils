__author__ = 'jaclu'

import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class Capturing(dict):
    """Usage:
        with Capturing() as output:
            do_something_that_prints_to_stdout_and_or_stderr()

        now output is a dict{'stdout:[],'stderr':[]}  with all the output line by line
    """

    def __enter__(self):
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        sys.stdout = self._mystdout = StringIO()
        sys.stderr = self._mystderr = StringIO()
        return self

    def __exit__(self, *args):
        self['stdout'] = self._mystdout.getvalue().splitlines()
        self['stderr'] = self._mystderr.getvalue().splitlines()
        sys.stdout = self._orig_stdout
        sys.stderr = self._orig_stderr

    def stdout(self):
        return self['stdout']

    def stderr(self):
        return self['stderr']

    def stdout_str(self):
        return ' '.join(self.stdout())