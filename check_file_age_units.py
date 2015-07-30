#!/usr/bin/env python

import glob
import os
import time

from naglib.nagiosplugin import NagiosPlugin
from naglib.timeunits import TimeUnits


class CheckFileAgeUnits(NagiosPlugin):
    VERSION = '3.4.2'  # 2015-04-19 jaclu trying to fix "Check output not found in output of MRPE" error
    HELP = """
Similar to standard plugin check_file_age, but here we can use units and not only use seconds
  default is seconds
    m   minutes
    h   hours
    d   days
    w   weeks
    m   months

  result will use same unit, no fractions only integer params like:
    12m    interperate as 12 minutes.

   -o --oldest if given selects oldest file matching filepath param
   -n --newest if given selects most recent file matching filepath param

   Currently -o / -n must point to a directory, coming versions should also
   support wildcarding a subset of the files in a directory
"""
    CMD_LINE_HINT = 'filepath'
    ARGC = '1'  # * = 0 or larger, n = exact match, 2+ two or more, 1-3 one to three

    def custom_options(self, parser):
        parser.add_option('-w', dest='age_warn')
        parser.add_option('-c', dest='age_crit')
        parser.add_option("-W", '--warn-on-missing', action="store_true", dest="missing_warn", default=False)
        parser.add_option('-s', '--size-min', dest='size_min', default=-1, type="int",
                          help='minimal size of file that is accepted')
        parser.add_option('-S', '--size-max', dest='size_max', default=-1, type="int",
                          help='maximum size of file that is accepted')
        parser.add_option("-o", '--oldest', action="store_true", dest="oldest", default=False,
                          help='if given selects oldest file matching filename')
        parser.add_option("-n", '--newest', action="store_true", dest="newest", default=False,
                          help='if given selects most recent file matching filename')

    def workload(self):
        # noinspection PyAttributeOutsideInit
        self.path_arg = self.args.pop()
        if self.options.newest and self.options.oldest:
            self.exit_help('Cant specify both oldest and newest - maximum one of them!')
        elif self.options.newest or self.options.oldest:
            # self.check_sorted_path()
            self.check_directory()
        else:
            self.check_one_file(self.path_arg)
        return

    def check_one_file(self, fname):
        self.log('file to check: %s' % fname, 1)

        if not os.path.exists(fname):
            msg = 'File not found: %s' % fname
            if self.options.missing_warn:
                self.exit_warn(msg)
            self.exit_crit(msg)

        size_check = (self.options.size_min > -1) or (self.options.size_max > -1)
        if size_check:
            self.ensure_size_is_ok(fname)

        warn = TimeUnits()
        if self.options.age_warn:
            try:
                warn = TimeUnits(self.options.age_warn)
            except:
                self.exit_help('invalid syntax for option -w: %s' % self.options.age_warn)
        crit = TimeUnits()
        try:
            crit = TimeUnits(self.options.age_crit)
        except:
            self.exit_help('invalid syntax for option -c: %s' % self.options.age_crit)

        if size_check and ((warn.value == 0) and (crit.value == 0)):
            self.exit_ok('file size good')

        if not self.options.age_crit:
            self.exit_crit('-c options must be specified!')
        if warn:
            self.log('warn level: %s' % warn.get(), 1)
        self.log('crit level: %s' % crit.get(), 1)

        if warn and (warn >= crit):
            self.exit_crit('warning age must be less than critical age')

        last_changed = os.stat(fname).st_mtime
        self.log('last changed timestamp for file: %s' % last_changed, 2)
        age = TimeUnits(time.time() - last_changed)
        self.add_perf_data('age', age.value, warn.value, crit.value, 0)
        self.log('File age: %s' % age, 2)
        msg = 'Age of file %s is %s' % (fname, age.get())
        if age > crit:
            self.exit_crit(msg)
        elif warn.value and (age > warn):
            self.exit_warn(msg)
        self.exit_ok(msg)

    def check_sorted_path(self):
        f = self.path_arg
        self.log('check_sorted_path(%s)' % f, lvl=1)
        files = sorted(glob.glob(f))
        if self.options.oldest:
            fname = files[0]
        else:
            fname = files[-1]
        return fname

    def check_directory(self):
        #
        wd = f = self.path_arg
        self.log('check_directory(%s)' % f, lvl=1)
        if f[-1] == os.path.sep:
            wd = os.path.dirname(f)
        elif os.path.isdir(f):
            wd = f
        else:
            self.exit_help('If -o or -n is used argument needs to be a directory')

        self.log('Will examine the following dir: %s' % wd, 3)
        os.chdir(wd)
        fname = self.safe_file_find_in_dir(wd)
        full_name = os.path.join(wd, fname)
        self.log('After checking a directory %s was chosen' % full_name, lvl=3)
        self.check_one_file(full_name)

    def safe_file_find_in_dir(self, wd):
        fname = ''
        if 0:  # sys.version >= '2.5':
            try:
                if self.options.oldest:
                    fname = min(os.listdir(wd), key=os.path.getmtime)
                else:
                    fname = max(os.listdir(wd), key=os.path.getmtime)
            except OSError(e):
                self.exit_crit('OSError: %s' % e)
            except:
                self.exit_crit('os.listdir() failed')
        else:
            # older python on some of our servers...
            files = sorted(os.listdir(wd), key=os.path.getmtime)
            if self.options.oldest:
                fname = files[0]
            else:
                fname = files[-1]
        return fname

    def ensure_size_is_ok(self, fname):
        size = os.path.getsize(fname)

        if self.options.size_min != -1:
            min_size = int(self.options.size_min)
        else:
            min_size = 0

        if self.options.size_max != -1:
            max_size = int(self.options.size_max)
        else:
            max_size = 0

        if min_size < 0:
            self.exit_crit("min_size can't be negative")
        if max_size < 0:
            self.exit_crit("max_size can't be negative")
        if max_size and (min_size > max_size):
            self.exit_crit('min_size must be less than max_size')

        if (self.options.size_min > -1) and (size < min_size):
            self.exit_crit('%s size (%i) under min: %i' % (fname, size, min_size))
        if (self.options.size_max > -1) and (size > max_size):
                self.exit_crit('%s size (%i) over max: %i' % (fname, size, max_size))
        return True


if __name__ == "__main__":
    CheckFileAgeUnits().run(standalone=True)

