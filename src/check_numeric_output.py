#!/usr/bin/env python

from src.naglib import NagiosPlugin


class CheckNumericOutput(NagiosPlugin):
    VERSION = '1.0.1'
    HELP = """
Runs a command with numerical output, and ensures result are in an acceptable
span (number is parsed as a float).

"""
    CMD_LINE_HINT = "cmd"

    def __init__(self, param_args=None):
        super(CheckNumericOutput, self).__init__(param_args)
        self.is_int = False

    def custom_options(self, parser):
        parser.add_option('-w', dest='min_warn', type="float", help='warning  if <= this')
        parser.add_option('-c', dest='min_crit', type="float", help='critical if <= this')
        parser.add_option("-W", dest="max_warn", type="float", help='warning  if >= this')
        parser.add_option("-C", dest="max_crit", type="float", help='critical if >= this')

    def workload(self):
        if len(self.args) != 1:
            self.exit_crit("You must specify a command to run (enclose with '' or \"\" if spaces are used)")
        self.params_are_sane()
        cmd = self.args[0]
        self.log('Command to run: %s' % cmd, 1)
        if not (self.options.min_crit or self.options.max_crit or self.options.min_warn or self.options.max_warn):
            self.exit_crit("You must specify at least one of -w -c -W -C")
        if self.options.min_crit and self.options.max_crit:
            if self.options.min_crit == self.options.max_crit:
                self.exit_crit("min_crit = max_crit")
        if self.options.min_warn and self.options.max_warn:
            if self.options.min_warn == self.options.max_warn:
                self.exit_crit("min_warn = max_warn")

        retcode, stdout, stderr = self.cmd_execute_output(cmd)
        self.log('retcode:\t%s' % retcode, 2)
        self.log('stdout:\t  %s' % stdout, 2)
        self.log('stderr:\t%s' % stderr, 2)
        if retcode:
            self.exit_crit("Exit code (%i) indicates failure" % retcode)
        if stderr:
            self.exit_crit("Output to stderr (%s) indicates failure" % stderr)
        try:
            result = float(stdout)
            self.is_int = result == int(stdout)
        except:
            self.exit_crit("Output (%s) not numeric!" % stdout)

        s_result = self.num_repr(result)
        msg = 'Output (%s)' % s_result + ' %s value - limit (%s)'
        if self.options.max_crit and (result >= self.options.max_crit):
            self.exit_crit(msg % ('high', self.num_repr(self.options.max_crit)))
        if self.options.min_crit and (result <= self.options.min_crit):
            self.exit_crit(msg % ('low', self.num_repr(self.options.min_crit)))
        if self.options.max_warn and (result >= self.options.max_warn):
            self.exit_warn(msg % ('high', self.num_repr(self.options.max_warn)))
            self.exit_warn(msg % ('warning high', self.num_repr(self.options.max_warn)))
        if self.options.min_warn and (result <= self.options.min_warn):
            self.exit_warn(msg % ('low', self.num_repr(self.options.min_warn)))
        self.exit_ok('Output %s' % s_result)

    def num_repr(self, value):
        if isinstance(value, int):
            r = '%i' % value
        else:
            r = '%f' % value
        return r

    def params_are_sane(self):
        min_warn = self.options.min_warn or 1
        min_crit = self.options.min_crit or 0
        max_warn = self.options.max_warn or self.options.max_warn or 999
        max_crit = self.options.max_crit or (max_warn + 1)
        if min_warn <= min_crit:
            self.exit_crit('min warn must be larger than min crit')
        if max_warn >= max_crit:
            self.exit_crit('max warn must be smaler than max crit')
        if min_warn > max_warn:
            self.exit_crit('min warn must be smaler than max warn')
        if min_crit > max_crit:
            self.exit_crit('min crit must be larger than max crit')
        return

if __name__ == "__main__":
    CheckNumericOutput().run(standalone=True)

