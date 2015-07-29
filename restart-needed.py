#!/usr/bin/env python

import os
import platform

from naglib.nagiosplugin import NagiosPlugin


class RestartNeeded(NagiosPlugin):
    VERSION = '1.0.2'
    HELP = """This is some more info on this specific plugin"""

    def workload(self):
        if platform.system() != 'Linux':
            self.exit_warn('This plugin is only meaningfull on Linux systems!')
        distname, version, iid = platform.dist()
        if distname not in ('Ubuntu', 'debian'):
            self.exit_warn('This distribution doesnt seem to be debian based (%s)' % distname)
        if os.path.isfile('/var/run/reboot-required'):
            self.exit_crit('System needs to be restarted')
        self.exit_ok('System does not need restarting')

if __name__ == "__main__":
    RestartNeeded().run(standalone=True)

