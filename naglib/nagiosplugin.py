#!/usr/bin/env python
import inspect
from optparse import OptionParser, IndentedHelpFormatter
import os.path
import subprocess
import sys
import time

# Exit statuses recognized by Nagios
NAG_UNKNOWN = -1
NAG_OK = 0
NAG_WARNING = 1
NAG_CRITICAL = 2

NAG_RESP_CLASSES = {
    NAG_UNKNOWN: 'UNKNOWN',
    NAG_OK: 'OK',
    NAG_WARNING: 'WARNING',
    NAG_CRITICAL: 'CRITICAL',
    }




class GenericRunner(object):
    VERSION = 'unknown' # override to something meaningfull

    CMD_LINE_HINT = '' # if given this will be printed after name [options]
    HELP = '' # add custom help if needed
    DESCRIPTION = None
    ARGC = '*' # * = 0 or larger, n = exact match, 2+ two or more, 1-3 one to three


    def __init__(self):
        self.option_handler()
        self.log_lvl = int(self.options.verbose)



    def custom_options(self, parser):
        """Override for adding local options.

        sample:
        parser.add_option('-H', '--hostname', dest='hostname')

        no return is expected
        """


    def workload(self):
        """
        workload() should always be terminated with: self.exit(code, msg)
        code is one of NAG_UNKNOWN NAG_OK NAG_WARNING NAG_CRITICAL
        msg is any oneliner msg
        """
        self.exit_crit('Plugin implementation must define a workload()!')


    def option_handler(self):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        prog_name = calframe[2][1]
        if self.CMD_LINE_HINT:
            usage = '%prog [options] ' + self.CMD_LINE_HINT
        else:
            usage = None
        self.parser = OptionParser(usage,
                                   description = self.DESCRIPTION,
                                   version=self.VERSION,
                                   )

        self.parser.add_option("-v", default=0, action="count", dest="verbose",
                               help='Verbosity level, you can add up to three -v \t\t0=no output, 1, 2, 3=all output')
        self.parser.add_option('-q', '--quiet', dest='verbose', action='store_false')

        self.custom_options(self.parser)
        try:
            self.options, self.args = self.parser.parse_args()
        except SystemExit,exit_code:
            if self.HELP:
                print self.HELP
            sys.exit(exit_code)
        self.verify_argcount()



    def exit_help(self,msg=None):
        "Convenient exit call, on param check failure"
        print
        if msg:
            print '***', msg
            print

        if self.options.verbose > 0:
            self.log('Defaults:')
            params = self.parser.defaults.keys()
            params.sort()
            for s in params:
                self.log('\t %s  %s' % (s, self.parser.defaults[s]))

        sys.argv.append('-h')
        self.parser.parse_args()



    def verify_argcount(self):
        argc = len(self.args)

        if self.ARGC == '*':
            return # anything goes

        #
        # Exact count
        #
        try:
            i = int(self.ARGC)
        except:
            i = -99
        if not (i == -99):
            # was single digit
            if not (argc == i):
                self.exit_help('This command must have exactly %i arguments' % i)
            return

        #
        # x+   x or more
        #
        if self.ARGC[-1] == '+':
            try:
                i = int(self.ARGC[:-1])
            except:
                i = -99
            if i == -99:
                self.exit_help('plugin bugg ARGC = "%s" is not accepted syntax' % self.ARGC)
            if argc < i:
                self.exit_help('to few arguments, at least %i required' % i)
            return

        #
        # x-y
        #
        l = self.ARGC.split('-')
        if len(l) > 1:
            imin = l[0]
            imax = l[1]
            if (argc < imin) or (argc>imax):
                self.exit_help('argument count outside accepted span (%s)' % self.ARGC)
            return
        return



    def log(self, msg, lvl=1):
        if lvl <= self.log_lvl:
            print msg
        return








class SubProcessTask(GenericRunner):
    PROC_TIMEOUT = 30

    def cmd_execute_output(self, cmd, timeout=PROC_TIMEOUT):
        "Returns retcode,stdout,stderr."
        if isinstance(cmd, (list, tuple)):
            cmd = ' '.join(cmd)
        self.log('External command: [%s]' % cmd, 3)
        self._cmd_std_out = u''
        self._cmd_std_err = u''
        try:
            t_fin = time.time() + timeout
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while p.poll() == None and t_fin > time.time():
                self._cmd_purge_io_buffers(p)
                time.sleep(0.1)

            if p.poll() == None:
                stderr = u'Timeout for command %s' % cmd
                self.log(u'*** %s' % stderr)
                self._cmd_purge_io_buffers(p)
                self.log(u'stdout: %s' % self._cmd_std_out)
                self.log(u'stderr: %s' % self._cmd_std_err)
                return 1,u'',stderr

            self._cmd_purge_io_buffers(p) # do last one to ensure we got everything
            retcode = p.returncode
            stdout = self._cmd_std_out
            stderr = self._cmd_std_err
        except:
            retcode = 1
            stdout = u''
            stderr = u'cmd_execute_output() exception - shouldnt normally happen'
        self.log(' exitcode: %i\n stdout: %s\n stderr: %s' % (retcode, stdout, stderr), 3)
        return retcode, stdout, stderr



    def cmd_execute1(self, cmd):
        "Returns 0 on success, or error message on failure."
        result = 0
        retcode, stdout, stderr = self.cmd_execute_output(cmd)
        if retcode or stdout or stderr:
            result = u'retcode: %s' % retcode
            if stdout:
                result += u'\nstdout: %s' % stdout
            if stderr:
                result += u'\nstderr: %s' % stderr
        return result



    def cmd_execute_abort_on_error(self, cmd, timeout=PROC_TIMEOUT):
        retcode, stdout, stderr = self.cmd_execute_output(cmd, timeout)
        if stderr:
            self.exit(NAG_CRITICAL, 'Errormsg: %s' % stderr)
        if retcode:
            self.exit(NAG_CRITICAL, 'Errorstatus: %i' % retcode)
        return stdout



    def _cmd_purge_io_buffers(self, p):
        try:
            s_out, s_err = p.communicate()
        except:
            return
        if s_out:
            self._cmd_std_out += s_out
        if s_err:
            self._cmd_std_err += s_err



class NagiosPlugin(SubProcessTask):
    """You must define a workload() that performs your check, when you are done
    call self.exit() with a nagios exit code and a short oneline msg, example:
    --------
    import os
    from nagiosplugin import NagiosPlugin, NAG_OK, NAG_WARNING, NAG_CRITICAL

    class FsTabChecker(NagiosPlugin):
        def workload(self):
            if os.path.isfile('/etc/fstab'):
                self.exit(NAG_OK, 'fstab is pressent')
            self.exit_crit( 'fstab is missing!')

    FsTabChecker().run()
    --------


    If you want to display seconds in the normal nagios text notation,
    I have included naglib.timeunits

    If you want to use perfdata, store it in self._perf_data
      Each entry is a tuple with the following components:
        A variable name (string)
        The current value of the variable (int or float)
        The warning level or ""
        The critical level or ""
        The minimum possible value or ""
        The maximum possible value or ""

      Only the variable name and the current value are mandatory.
      Insert and empty string if you want to skip an unneeded value.
      Trailing empty strings can be left out.
      Sample item: ('load1', '1.150', '2.000', '5.000','0')
    """

    BASE_VERSION = '1.5.0'  # split this up in three subclasses
    VERSION = BASE_VERSION
    MSG_LABEL = '' # optional prefix for the message line




    def __init__(self):
        super(NagiosPlugin,self).__init__()
        self._perf_data = []



    def run(self):
        try:
            self.workload()
            self.exit_crit('Plugin implementation failed to terminate properly!')
        except SystemExit:
            raise # normal exit, system requested to terminate
        except:
            self.exit_crit('Plugin implementation crashed!')




    def add_perf_data(self, name, value, warning='', critical='',minimum='', maximum=''):
        extra_data = []
        for x in (warning, critical, minimum, maximum):
            extra_data.append(self._perf_value(x))
        while extra_data and extra_data[-1] == '':
            extra_data.pop(-1)
        self._perf_data.append((name, self._perf_value(value)) + tuple(extra_data))



    def exit_ok(self, msg):
        self.exit(NAG_OK, msg)

    def exit_warn(self, msg):
        self.exit(NAG_WARNING, msg)


    def exit_crit(self, msg):
        self.exit(NAG_CRITICAL, msg)


    def exit(self, code, msg):
        # perfdata should be printed after a pipe char, somewhat like this:
        # OK - load average: 1.15, 0.83, 0.49|load1=1.150;2.000;5.000;0; load5=0.830;2.000;5.000;0; load15=0.490;2.000;5.000;0;
        if not code in NAG_RESP_CLASSES.keys():
            self.exit_crit('Bad exit code: %s' % code)
        s_code = NAG_RESP_CLASSES[code]
        if self.MSG_LABEL:
            msg = '%s %s' % (self.MSG_LABEL, msg)
        if self._perf_data:
            msg += "|"
            perfs = []
            for item in self._perf_data:
                perfs.append('%s=' % item[0] + ';'.join(item[1:]))

            msg += '; '.join(perfs) + ';'

        #print '%s: %s' % (s_code, msg)
        print msg
        raise SystemExit, code



    def _perf_value(self, value):
        if isinstance(value, float):
            r = '%.2f' % value
        else:
            r = str(value)
        return r




