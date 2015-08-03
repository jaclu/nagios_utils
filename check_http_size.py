#!/usr/bin/env python
"""
If you cant install the nagios check_http you can use this instead...

"""

import time
try:
    from urllib2 import urlopen, HTTPError
except:
    # python3
    from urllib.request import urlopen
    from urllib.error import HTTPError


from naglib.nagiosplugin import NagiosPlugin


class CheckHttpSize(NagiosPlugin):
    VERSION = '1.1.0'  # added single param option
    DESCRIPTION = "Checks that requested document size is within bounds"
    CMD_LINE_HINT = 'url'
    HELP = """
    At least one of -w or -c must be given, and the notation is min:max or a single exact number
    Any size outside this will trigger an alarm.

    If response is not received within timeout period, an alarm is triggered
    """

    def custom_options(self, parser):
        parser.add_option("-w", '--warning', dest="warning", help="syntax:  min:max")
        parser.add_option("-c", '--critical', dest="critical", help="syntax:  min:max")
        parser.add_option("-t", '--timeout', dest="timeout", default=10, type="int")

    def workload(self):
        size_min = size_max = 0
        size_warn = size_crit = ''
        if len(self.args) < 1:
            self.exit_crit('Mandatory param missing')
        url = self.args[0]
        if not (self.options.warning or self.options.critical):
            self.exit_crit('-w or -c must be given')

        if self.options.warning:
            w1, w2 = self.verify_size_span(self.options.warning, 'warning')
            size_min = w1
            size_max = w2
            size_warn = w2

        if self.options.critical:
            c1, c2 = self.verify_size_span(self.options.critical, 'critical')
            size_crit = c2
        doc = self.check_url(url, timeout=self.options.timeout)
        size = len(doc)

        self.add_perf_data('size', size, warning=size_warn, critical=size_crit)
        if self.options.critical:
            if size < c1 or size > c2:
                self.exit_crit('%i is out of range' % size)
        if self.options.warning:
            if size < w1 or size > w2:
                self.exit_warn('%i is out of range' % size)

        self.exit_ok('Acceptable doc size: %i' % size)

    def check_url(self, url, s_expect='', timeout=10):
        t1 = time.time()
        try:
            f = urlopen(url, timeout=timeout)
        except HTTPError as e:
            self.exit_crit('HTTP error:%i - %s' % (e.code, e.msg))
        except:
            if time.time() > t1 + timeout:
                self.exit_crit('timeout!')
            self.exit_crit('unknown failure processing url')
        if f.code != 200:
            self.exit_crit('%s %s' % (f.code, f.msg))
        content = f.read()
        if s_expect and (content.find(s_expect) < 0):
            self.exit_crit('%s not found' % s_expect)
        return content

    def verify_size_span(self, param, label):
        try:
            parts = param.split(':')
        except:
            self.exit_help('bad syntax for %s - %s' % (label, param))
        if len(parts) == 1:
            m1 = m2 = parts[0]
        elif not len(parts) == 2:
            self.exit_help('there should be 1 or 2 numbers given for %s - %s' % (label, param))
        else:
            m1 = parts[0]
            m2 = parts[1]
        try:
            m1 = int(m1)
        except:
            self.exit_help('value (%s) is not a number, %s - %s' % (m1, label, param))
        try:
            m2 = int(m2)
        except:
            self.exit_help('value (%s) is not a number, %s - %s' % (m2, label, param))
        if m1 > m2:
            self.exit_help('second number must be larger than first, %s - %s' % (label, param))

        return m1, m2


if __name__ == "__main__":
    CheckHttpSize().run(standalone=True)

