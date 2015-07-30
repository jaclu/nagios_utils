#!/usr/bin/env python

from naglib.nagiosplugin import NagiosPlugin
from naglib.timeunits import TimeUnits

import time
import os
import stat


def file_age_in_seconds(pathname):
    return time.time() - os.stat(pathname)[stat.ST_MTIME]


class ThumblrSyncBackLog(NagiosPlugin):
    VERSION = '1.1.3'  # 2015-03-25 jaclu added perfdata
    DESCRIPTION = "Warns if back-log of thumblr2 files is to large, or oldest file waiting is to old"
    CMD_LINE_HINT = '/path/to/sync-wait-directory'

    def __init__(self, param_args=None):
        super(ThumblrSyncBackLog, self).__init__(param_args)
        self.sync_dir = '/tmp'  # will be changed in workload()

    def custom_options(self, parser):
        parser.add_option("-w", '--warning',   type="int", dest="size_warn", default=25000)
        parser.add_option("-c", '--crtitical', type="int", dest="size_crit", default=100000)
        parser.add_option("-a", '--age', dest="max_age", default='1d',
                          help='max allowed age for a sync file, either seconds or suffix it with a unit '
                               '(m)inutes (h)ours) (d)ays (w)eeks example 2d (2 days)')

    def workload(self):
        if len(self.args) != 1:
            self.exit_help('Missing path to sync-wait-directory!')
        self.sync_dir = self.args.pop()
        if not os.path.isdir(self.sync_dir):
            self.exit_help('%s is not a valid directory!' % self.sync_dir)
        try:
            age_max = TimeUnits(self.options.max_age)
        except:
            self.exit_help('invalid syntax for option -a: %s' % self.options.max_age)

        self.log('sync-dir to check: %s' % self.sync_dir, 1)
        self.log('    size  warning: %s' % self.options.size_warn, 1)
        self.log('    size critical: %s' % self.options.size_crit, 1)

        cmd = 'wc %s/* | tail -n 1' % self.sync_dir
        try:
            output = self.cmd_execute1(cmd)
            if output.find('No such file or directory') > -1:
                count = 0
            else:
                count = int(output.split('stdout:')[1].split()[0])
        except:
            self.exit_crit('Bad cmd output: [%s]' % output.strip())

        self.add_perf_data('items', count, self.options.size_warn, self.options.size_crit, '0')

        oldest_file, oldest_age = None, 0
        for filename in os.listdir(self.sync_dir):
            file_path = os.path.join(self.sync_dir, filename)
            file_age = time.time() - os.stat(file_path).st_mtime
            if file_age > oldest_age or oldest_age is None:
                oldest_file, oldest_age = filename, file_age
        self.add_perf_data('oldest', oldest_age, '', age_max.value, 0)

        if count > self.options.size_crit:
            self.exit_crit('%i exceedes critical level: %i' % (count, self.options.size_crit))
        if count > self.options.size_warn:
            self.exit_warn('%i exceedes warning level: %i' % (count, self.options.size_warn))
        ok_msg = '%i items in backlog' % count

        if oldest_age:
            t_oldest = TimeUnits(oldest_age)
            if t_oldest > age_max:
                self.exit_crit('%s older than %s [%s]' % (os.path.join(self.sync_dir, oldest_file), age_max, t_oldest))
            ok_msg += ', no file older than %s' % t_oldest

        self.exit_ok(ok_msg)


if __name__ == "__main__":
    ThumblrSyncBackLog().run(standalone=True)

