#!/usr/bin/env python
"""
If you cant install the nagios check_http you can use this instead...

"""

import time

from src.naglib import NagiosPlugin


class CheckAlternateHttp(NagiosPlugin):
    VERSION = '1.3.2'  # added param -n

    def custom_options(self, parser):
        parser.add_option("-u", '--url', dest="url")
        parser.add_option("-r", '--response', dest="response")
        parser.add_option("-n", '--not_allowed', dest="not_allowed", action="store_true", default=False,
                          help='finding the response results in critical')

    def workload(self):
        if not self.options.url:
            self.exit_crit('No url specified')
        if not self.options.response:
            self.exit_crit('No response specified')

        s_expect = self.options.response
        t1 = time.time()
        html = self.url_get(self.options.url)
        t2 = time.time() - t1
        self.add_perf_data('response time', t2)
        is_found = html.find(s_expect) > -1
        if self.options.not_allowed and is_found:
            self.exit_crit('"%s" should not be present' % s_expect)
        elif not is_found and (not self.options.not_allowed):
            self.exit_crit('"%s" should be present' % s_expect)
        if self.options.not_allowed:
            msg = 'banned string not found'
        else:
            msg = 'expected string found'
        self.exit_ok('%s in %.2f seconds' % (msg, t2))


if __name__ == "__main__":
    CheckAlternateHttp().run(standalone=True)

