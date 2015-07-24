#!/usr/bin/env python
"""
If you cant install the nagios check_http you can use this instead...

"""

import time
import urllib2

from naglib.nagiosplugin import NagiosPlugin


class CheckHttp(NagiosPlugin):
    VERSION = '1.3.2'  # added param -n

    def custom_options(self, parser):
        parser.add_option("-u", '--url', dest="url")
        parser.add_option("-r", '--response', dest="response")
        parser.add_option("-n", '--not_allowed', dest="not_allowed", action="store_true", default=False,
                          help='finding the response results in critical')

    def workload(self):
        if not self.options.url:
            self.exit_help('No url specified')
        if not self.options.response:
            self.exit_help('No response specified')

        if self.options.verbose > 1:
            print 'url: %s' % self.options.url
            if self.options.response:
                print 'expected response: %s' % self.options.response
        t1 = time.time()
        self.check_url(self.options.url, self.options.response)
        t2 = time.time() - t1
        self.add_perf_data('response time', t2)
        self.exit_ok('Expected result received in %.2f seconds' % t2)

    def check_url(self, url, s_expect, timeout=10):
        t1 = time.time()
        try:
            f = urllib2.urlopen(url, timeout=timeout)
        except urllib2.HTTPError, e:
            self.exit_crit('HTTP error:%i - %s' % (e.code, e.msg))
        except:
            if time.time() > t1 + timeout:
                self.exit_crit('timeout!')
            self.exit_crit('unknown failure processing url')
        if f.code != 200:
            self.exit_crit('%s %s' % (f.code, f.msg))
        content = f.read()
        is_found = content.find(s_expect) > -1
        if self.options.not_allowed and is_found:
            self.exit_crit('"%s" should not be present' % s_expect)
        elif not is_found and (not self.options.not_allowed):
            self.exit_crit('"%s" should be present' % s_expect)
        if self.options.not_allowed:
            msg = 'banned string not found'
        else:
            msg = 'expected string found'
        self.exit_ok(msg)


if __name__ == "__main__":
    CheckHttp().run(standalone=True)

