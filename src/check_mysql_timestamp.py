#!/usr/bin/env python

import datetime

from naglib.nagiosplugin import NagiosPlugin
from src.naglib.timeunits import TimeUnits


# TODO write unittests
class CheckMysqlTimeStampAge(NagiosPlugin):
    VERSION = '0.1.1'
    HELP = """
Similar to standard plugin check_file_age, but here we can use units and not only use seconds
  defaul is seconds
    m   minutes
    h   hours
    d   days
    w   weeks
    m   months

  result will use same unit, no fractions only integer params like:
    12m    interperete as 12 minutes,
"""

    def custom_options(self, parser):
        parser.add_option('-w', dest='age_warn')
        parser.add_option('-c', dest='age_crit')
        parser.add_option('-m', dest='query', help='mysql query to run')
        parser.add_option('-d', dest='db', help='mysql database')

    def workload(self):
        if not self.options.query:
            self.exit_crit('-m option must be specified!')
        if not self.options.db:
            self.exit_crit('-d option must be specified!')
        if not (self.options.age_crit and self.options.age_warn):
            self.exit_crit('-w and -c options must be specified!')
        warn = TimeUnits(self.options.age_warn)
        crit = TimeUnits(self.options.age_crit)
        self.log('mysql query to run: %s' % self.options.query, 1)
        self.log('warn level: %s' % warn.get(), 1)
        self.log('crit level: %s' % crit.get(), 1)
        if warn >= crit:
            self.exit_crit('warning age must be less than critical age')
        retcode, stdout, stderr = self.cmd_execute_output(
            'echo "%s" | mysql %s | tail -n 1' % (self.options.query, self.options.db))
        if retcode:
            self.exit_crit('mysql failed: %s' % stderr)
        dt = datetime.datetime.strptime(stdout.strip(), '%Y-%m-%d %H:%M:%S')
        age = TimeUnits(date_time=dt)
        self.log('mysql timestamp: %s' % age, 2)
        msg = 'timestamp is %s old' % age.get()
        if age > crit:
            self.exit_crit(msg)
        elif age > warn:
            self.exit_warn(msg)
        self.exit_ok(msg)

if __name__ == "__main__":
    CheckMysqlTimeStampAge().run(standalone=True)

