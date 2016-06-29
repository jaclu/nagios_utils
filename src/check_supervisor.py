#!/usr/bin/env python


import tempfile

from naglib.nagiosplugin import NagiosPlugin


# TODO write unittests
class CheckSupervisor(NagiosPlugin):
    VERSION = '0.0.3'
    DESCRIPTION = "Checks if supervisor is running"

    def workload(self):
        cmd = 'ps axu |grep supervisord | grep -v grep'

        retcode, stdout, stderr = self.cmd_execute_output(cmd)
        if stderr:
            self.exit_crit(stderr)
        elif retcode:
            self.exit_crit('supervisord is not running!')
        self.exit_ok('supervisor is running: [%s] %i' % (stdout, len(stdout)))

if __name__ == "__main__":
    CheckSupervisor().run(standalone=True)
