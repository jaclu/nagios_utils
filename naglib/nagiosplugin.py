#!/usr/bin/env python

try:
    from exceptions import StandardError
except:
    pass  # was py3
import inspect
from optparse import OptionParser
import subprocess
import sys
import time

import requests


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

NAG_MESSAGES = {
    NAG_UNKNOWN: 'UNKNOWN',
    NAG_OK: 'OK',
    NAG_WARNING: 'WARN',
    NAG_CRITICAL: 'CRIT',

}


class GenericRunner(object):
    VERSION = 'unknown'  # override to something meaningfull

    CMD_LINE_HINT = ''  # if given this will be printed after name [options]
    HELP = ''  # add custom help if needed
    DESCRIPTION = None
    ARGC = '*'  # * = 0 or larger, n = exact match, 2+ two or more, 1-3 one to three

    def __init__(self, param_args=None):
        self.log_lvl = 1  # initial value used during option_handler
        self._standalone_mode = True  # might be changed in run()
        self._result = None
        self._perf_data = []
        self.option_handler(param_args)
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

    def option_handler(self, param_args=None):
        if self.CMD_LINE_HINT:
            usage = '%prog [options] ' + self.CMD_LINE_HINT
        else:
            usage = None
        self.parser = OptionParser(usage,
                                   description=self.DESCRIPTION,
                                   version=self.VERSION,
                                   )

        self.parser.add_option("-v", default=0, action="count", dest="verbose",
                               help='Verbosity level, you can add up to three -v \t\t0=no output, 1, 2, 3=all output')
        self.parser.add_option('-q', '--quiet', dest='verbose', action='store_false')
        self.parser.add_option('--nsca', dest='nsca', default='',
                               help='show result in nsca format, expected param host,srvcname '
                                    '(host where the check is logged), '
                                    'nsca will find destination where to send the data in its own config file)')

        self.custom_options(self.parser)
        if not param_args:
            # if we have param_args this is irrelevant
            if sys.argv[0].find('py.test') > -1:
                sys.argv = [inspect.stack()[4][1]] # during pytest insert progname here
            elif sys.argv[0].find('utrunner.py') > -1:
                sys.argv = [inspect.stack()[4][1]] # during pytest insert progname here
        try:
            self.options, self.args = self.parser.parse_args(param_args)
        except SystemExit as exit_code:
            if self.HELP:
                self.log(self.HELP)
            raise #SystemExit(0) # exiting program after displaying help

    def NOT_exit_help(self, msg=None):
        """Convenient exit call, on param check failure"""
        self.parser.print_help()  # trigger a help printout
        self.log('', 0)

        if self.options.verbose > 0:
            self.log('Defaults:')
            params = self.parser.defaults.keys()
            params.sort()
            for s in params:
                self.log('\t %s  %s' % (s, self.parser.defaults[s]))
        if msg:
            self.log('*** %s' % msg, 0)
        self.exit_crit('bad param')

    def url_get(self, host, url='/'):
        if host.find('http') < 0:
            host = 'http://' + host
        try:
            u = ('%s%s' % (host, url)).strip()
            page = requests.get(u)
        except requests.exceptions.ConnectionError as e:
            self.exit_crit('Connection error')
        except requests.exceptions.Timeout as e:
            self.exit_warn('Timeout')
        except:
            self.exit_crit('Unknown request error')
            # TODO: this should not be here...
            self.exit_crit('Failed to retrieve revision data')
        if not page.status_code == 200:
            self.exit_crit('HTML response not 200')
        html = page.text
        return html

    def log(self, msg, lvl=1):
        if lvl <= self.log_lvl:
            print(msg)
        return

    def exit_ok(self, msg):
        self._exit(NAG_OK, '%s: %s' % (NAG_MESSAGES[NAG_OK], msg))

    def exit_warn(self, msg):
        self._exit(NAG_WARNING, '%s: %s' % (NAG_MESSAGES[NAG_WARNING], msg))

    def exit_crit(self, msg):
        self._exit(NAG_CRITICAL, '%s: %s' % (NAG_MESSAGES[NAG_CRITICAL], msg))

    def _exit(self, code, msg):
        if code not in NAG_RESP_CLASSES.keys():
            self.exit_crit('Bad exit code: %s' % code)
        s_code = NAG_RESP_CLASSES[code]
        if self._perf_data:
            msg += "|"
            perfs = []
            for item in self._perf_data:
                perfs.append('%s=' % item[0] + ';'.join(item[1:]))

            msg += '; '.join(perfs) + ';'

        if self._standalone_mode:
            if self.options.nsca:
                response = '\t'.join(self.options.nsca.split(',') + ['%s' % code] + [msg]
                                     ) + '\n'
                self.log(response, 0)
                sys.exit(0)  # we show exit_code in nsca output

            if self.options.verbose == 0:
                self.log(msg, 0)
            else:
                self.log('code:%i \t%s' % (code, msg), lvl=1)
        else:
            self._result = (code, msg)

        sys.exit(code)


class SubProcessTask(GenericRunner):
    PROC_TIMEOUT = 30

    def __init__(self, param_args=None):
        super(SubProcessTask, self).__init__(param_args)
        self._cmd_std_out = u''
        self._cmd_std_err = u''

    def cmd_execute_output(self, cmd, timeout=PROC_TIMEOUT):
        """Returns retcode,stdout,stderr."""
        if isinstance(cmd, (list, tuple)):
            cmd = ' '.join(cmd)
        self.log('External command: [%s]' % cmd, 3)
        try:
            t_fin = time.time() + timeout
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while p.poll() is None and t_fin > time.time():
                time.sleep(0.1)

            if p.poll() is None:
                stderr = u'Timeout for command %s' % cmd
                self.log(u'*** %s' % stderr)
                self._cmd_purge_io_buffers(p)
                self.log(u'stdout: %s' % self._cmd_std_out)
                self.log(u'stderr: %s' % self._cmd_std_err)
                return 1, u'', stderr

            self._cmd_purge_io_buffers(p)  # do last one to ensure we got everything
            retcode = p.returncode
            stdout = self._cmd_std_out
            stderr = self._cmd_std_err
        except:
            retcode = 1
            stdout = u''
            stderr = u'cmd_execute_output() exception - shouldnt normally happen'
        self.log(' exitcode: %i\n stdout: %s\n stderr: %s' % (retcode, stdout, stderr), 3)
        return retcode, stdout, stderr

    def cmd_execute1(self, cmd, timeout=PROC_TIMEOUT):
        """Returns 0 on success, or error message on failure."""
        result = 0
        retcode, stdout, stderr = self.cmd_execute_output(cmd, timeout)
        if retcode or stdout or stderr:
            result = u'retcode: %s' % retcode
            if stdout:
                result += u'\nstdout: %s' % stdout
            if stderr:
                result += u'\nstderr: %s' % stderr
        return result

    def cmd_execute_raise_on_error(self, cmd, timeout=PROC_TIMEOUT):
        retcode, stdout, stderr = self.cmd_execute_output(cmd, timeout)
        if retcode or stderr:
            raise Exception('cmd [%s] failed' % cmd)
        return True

    def cmd_execute_abort_on_error(self, cmd, timeout=PROC_TIMEOUT):
        retcode, stdout, stderr = self.cmd_execute_output(cmd, timeout)
        if stderr:
            self.exit_crit('Errormsg: %s' % stderr)
        if retcode:
            self.exit_crit('Errorstatus: %i' % retcode)
        return stdout

    def _cmd_purge_io_buffers(self, p):
        try:
            s_out, s_err = p.communicate()
        except:
            return
        if s_out:
            self._cmd_std_out += s_out.decode("utf-8")
        if s_err:
            self._cmd_std_err += s_err.decode("utf-8")
        return


def _perf_value(value):
    if isinstance(value, (float, int)):
        r = '%.2f' % value
    else:
        #raise SyntaxError('Doesnt seem numeric: [%s]' % value)
        r = ''
    return r


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

    BASE_VERSION = '1.6.1'  # added nsca global option
    VERSION = BASE_VERSION
    MSG_LABEL = ''  # optional prefix for the message line
    NO_PARAMS_ERROR = '' # set this if no params triggers error

    def __init__(self, param_args=None):
        super(NagiosPlugin, self).__init__(param_args)
        # self._standalone_mode = False  TODO almost certain this should go...

    def run(self, standalone=False, ignore_verbose=False):
        self._standalone_mode = standalone
        if ignore_verbose:
            self.log_lvl = 0
        try:
            self.show_options()
            self.verify_argcount()
            self.workload()
            self.exit_crit('Plugin implementation failed to terminate properly!')
        except SystemExit:
            # normal exit, system requested to terminate
            if self._standalone_mode:
                raise  # honors the sys.exit(code) call...
            else:
                return self._result
        except:
            self.exit_crit('Plugin implementation crashed!')
        return

    def show_options(self):
        if self.log_lvl < 1:
            return
        self.log('Options for program (* indicates default)')
        optlst = self.options.__dict__
        opts = []
        for s in optlst.keys():
            value = optlst[s]
            if value == self.parser.defaults[s]:
                value = '*%s' % value
            opts.append('  %s = %s ' % (s, value))
        opts.sort()
        for o in opts:
            self.log(o, 0)
        if self.args:
            self.log('  Args: %s' % ' '.join(self.args), 0)
        return

    def add_perf_data(self, name, value, warning='', critical='', minimum='', maximum=''):
        extra_data = []
        for x in (warning, critical, minimum, maximum):
            extra_data.append(_perf_value(x))
        while extra_data and extra_data[-1] == '':
            extra_data.pop(-1)
        self._perf_data.append((name, _perf_value(value)) + tuple(extra_data))


    def verify_argcount(self):
        argc = len(self.args)

        if self.ARGC == '*':
            return  # anything goes

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
                self.exit_crit('This command must have exactly %i arguments' % i)
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
            if (argc < imin) or (argc > imax):
                self.exit_help('argument count outside accepted span (%s)' % self.ARGC)
            return
        return



