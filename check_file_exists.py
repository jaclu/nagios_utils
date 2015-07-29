#!/usr/bin/env python

import os
import time

from naglib.nagiosplugin import NagiosPlugin, NAG_WARNING, NAG_CRITICAL, NAG_OK, NAG_RESP_CLASSES, NAG_MESSAGES
from naglib.timeunits import TimeUnits


class CheckFileExists(NagiosPlugin):
    VERSION = '1.1'  # 2015-03-25 jaclu added perfdata
    HELP = """
Returns critical if file is missing
  -w makes the alarm be a warning instead of critical.
  -r negates the check crit/warn is returned if file exists

"""

    def custom_options(self, parser):
        parser.add_option("-w", '--warn-on-missing', action="store_true", dest="missing_warn", default=False)
        parser.add_option("-r", '--reverse-check', action="store_false", dest="file_should_exist", default=True)

    def workload(self):
        if len(self.args) != 1:
            self.exit_crit('exactly one filename must be supplied as param')

        fname = self.args.pop()

        if self.options.missing_warn:
            failure = NAG_WARNING
        else:
            failure = NAG_CRITICAL

        self.log('file to check: %s' % fname, 1)
        self.log('\tshould file exist: %s' % self.options.file_should_exist, 2)
        self.log('\tfailure reported as warning: %s' % self.options.missing_warn, 2)
        file_is_found = os.path.exists(fname)
        perf_value = '0.0'
        result = failure
        if file_is_found:
            perf_value = time.time() - os.path.getmtime(fname)
            if self.options.file_should_exist:
                result = NAG_OK
                msg = 'OK: %s was found'
            else:
                result = failure
                msg = NAG_MESSAGES[failure] + ': %s should not be present'
        else:  # not found
            if self.options.file_should_exist:
                result = failure
                msg = NAG_MESSAGES[failure] + ': %s not present'
            else:
                result = NAG_OK
                msg = 'OK: %s not present'

        self.add_perf_data('file age', perf_value, '', '', '0')
        self._exit(result, msg % fname)


if __name__ == "__main__":
    CheckFileExists().run(standalone=True)

