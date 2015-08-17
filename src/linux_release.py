#!/usr/bin/env python

import platform

from src.naglib import NagiosPlugin


# TODO write unittests
class LinuxRelease(NagiosPlugin):
    VERSION = '1.0.2'
    HELP = """This is some more info on this specific plugin"""

    def workload(self):
        if platform.system() != 'Linux':
            self.exit_warn('This plugin is only meaningfull on Linux systems!')

        retcode, stdout, stderr = self.cmd_execute_output('lsb_release -a')
        if retcode:
            self.exit_crit('lsb_release command failed!')
        try:
            s = stdout.split('Description:')[1].split('Release:')[0]
            release_string = s.strip()
        except:
            self.exit_crit('Failed to parse release string')
        self.exit_ok(release_string)

if __name__ == "__main__":
    LinuxRelease().run(standalone=True)

