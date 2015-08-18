#!/usr/bin/python

import time

import numpy

from naglib import NagiosPlugin


def line_cleanup(org_line):
    line = ''
    esc_mode = False
    for c in org_line:
        if c == '\x1b':
            esc_mode = True
        if esc_mode and c == 'm':
            esc_mode = False
            continue  # dont store the m char
        if not esc_mode:
            line += c
    return line.strip()


# TODO write unittests
class CheckCfApp(NagiosPlugin):
    VERSION = '1.4.1'  # added ping timeout stats update
    HELP = """
Monitors a cloud fusion app for important stats
  -w warning  load level (default is 50)
  -c critical load level (default is 90)
  -C command used to interact with Cloud Foundry (default is 'cf')
  -i fewer running instances triggers warning
  -I fewer running instances triggers critical
"""

    def custom_options(self, parser2):
        parser2.add_option('-w', '--warning', dest='warning_load', type='float', default=50)
        parser2.add_option('-c', '--critical', dest='critical_load', type='float', default=90)
        parser2.add_option("-C", '--command', dest='command', default='cf')
        parser2.add_option("-s", '--space', dest='space')
        parser2.add_option('-i', '--inst-warn', dest='warn_instances', type='int', default=0)
        parser2.add_option('-I', '--inst-crit', dest='crit_instances', type='int', default=0)
        parser2.add_option("-p", '--ping', action="store_true", dest="do_ping", default=False)

    def workload(self):
        stdout = ''
        if len(self.args) != 1:
            self.exit_crit('exactly one appname must be supplied as param')
        appname = self.args.pop()

        if not self.options.command:
            self.exit_crit('param command empty!')

        if self.options.space:
            cmd = '%s target -s %s' % (self.options.command, self.options.space)
            self.log('Will change space to  %s' % self.options.space)
            stdout = self.cmd_execute_abort_on_error(cmd)

        cmd = '%s app %s' % (self.options.command, appname)
        self.log('Will run cf app',)
        t1 = time.time()
        try:
            stdout = self.cmd_execute_abort_on_error(cmd, 10)
        except:
            t2 = time.time() - t1
            self.add_perf_data('response time', t2, 5, 20, '0')
            self.exit_crit('Cmd failed!!')
        t2 = time.time() - t1
        if self.options.do_ping:
            self.add_perf_data('response time', t2, 5, 20, '0')
            self.exit_ok('Response time logged')

        loads = []
        max_load = inst_count = run_count = 0
        for org_line in stdout.split('\n'):
            self.log('Orgline: %s' % org_line, 4)
            line = line_cleanup(org_line)
            self.log('Unescaped line: %s' % line, 4)
            if not line or line[0] != '#':
                continue
            inst_count += 1
            parts = line.split()

            status = parts[1]
            if status == 'running':
                run_count += 1

            """ Not used yet
            ddate = parts[2]
            ttime = parts[3]
            if parts[4] == 'PM':
                time_parts = ttime.split(':')
                time_parts[0] = '%i' % (int(time_parts[0]) + 12)
                ttime = ':'.join(time_parts)
            """
            load = float(parts[5][:-1])  # skip % char
            loads.append(load)
            if load > max_load:
                max_load = load

        if not run_count:
            self.exit_warn('No instances running!')

        avg_load = numpy.mean(loads)  # TODO cast to right type
        msg = 'Instances:%i/%i maxload:%.1f avgload:%.1f' % (run_count, inst_count, max_load, avg_load)
        self.add_perf_data('maxload', max_load, self.options.warning_load, self.options.critical_load, '0')
        self.add_perf_data('avgload', avg_load, self.options.warning_load, self.options.critical_load, '0')
        if max_load >= self.options.critical_load:
            self.exit_crit(msg + ' ERR: load max_load over limit!')
        if run_count < self.options.crit_instances:
                self.exit_crit(msg + ' ERR: too few running instances!')
        if run_count < self.options.warn_instances:
            self.exit_warn(msg + ' WARN: too few running instances!')
        if max_load >= self.options.warning_load:
            self.exit_warn(msg + ' WARN: load max_load over limit!')
        self.exit_ok(msg)


if __name__ == "__main__":
    CheckCfApp().run(standalone=True)
