#!/usr/bin/env python
"""
If you want to bundle this with nsca you could could trigger it from crontab with a script something like this:
--------------------
#!/bin/sh

TMP_FILE=/tmp/NSCA_ApiApps-output

/usr/local/nagiosplugins/check_a9_api.py --nsca <host>,<svc_description> apps > $TMP_FILE
cat  $TMP_FILE | /usr/sbin/send_nsca -H <nagios_host>
--------------------
"""
__author__ = 'jaclu'

import time
import os

from naglib.nagiosplugin import NagiosPlugin
from naglib.timeunits import TimeUnits


def extract_cloud_foundry_error_details(s):
    parts = s.split('FAILED')
    if len(parts) < 2:
        r = ''  # nothing found
    else:
        r = parts[1]
    return r.strip()

# TODO complete unittests
class CheckAny9Api(NagiosPlugin):
    VERSION = '1.0.0'
    CMD_LINE_HINT = 'if you need to use - for options to the cf command encapsulate like "push -f manifest.yml"'

    def custom_options(self, parser):
        parser.add_option('-w', '--warning',   dest='warning',   type='int', default=30)
        parser.add_option('-c', '--critical',  dest='critical',  type='int', default=60)
        parser.add_option("-t", '--timeout',   dest='timeout',   type='int', default=300)
        parser.add_option("-C", '--command',   dest='command',   default='cf')
        parser.add_option("-e", '--errvalue',  dest='errvalue',  type='int', default=-10,
                          help='if cmd timeouts or otherwise fail, this is perf value to send')
        parser.add_option("-d", '--directory', dest="directory", default='',
                          help='cd to this location before executing')

    def workload(self):
        args = ' '.join(self.args)
        if self.options.directory:
            os.chdir(self.options.directory)

        cmd = '%s  %s' % (self.options.command, args)
        self.log('Will run %s' % cmd,)
        t1 = time.time()
        retcode, stdout, stderr = self.cmd_execute_output(cmd, self.options.timeout)
        if stderr and stderr.split()[0] == 'Timeout':
            self.add_perf_data('response time', self.options.errvalue, warning=self.options.warning,
                               critical=self.options.critical, minimum=self.options.errvalue)
            self.exit_crit('Timeout!')

        t2 = time.time() - t1
        if stderr or retcode:
            self.log('cmd took %.2f seconds' % t2)  # since perf data wont show it...
            err_details = extract_cloud_foundry_error_details(stdout)
            self.add_perf_data('response time', self.options.errvalue, warning=self.options.warning,
                               critical=self.options.critical, minimum=self.options.errvalue)
            self.exit_crit('Errormsg: %s' % err_details or stderr)

        self.add_perf_data('response time', t2, warning=self.options.warning, critical=self.options.critical,
                           minimum=self.options.errvalue)
        msg = 'API cmd took %s' % TimeUnits(t2)
        if t2 < self.options.warning:
            self.exit_ok(msg)
        elif t2 < self.options.critical:
            self.exit_warn(msg)
        else:
            self.exit_crit(msg)


if __name__ == "__main__":
    CheckAny9Api().run(standalone=True)
