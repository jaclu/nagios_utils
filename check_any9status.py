#!/usr/bin/env python
"""
If you cant install the nagios check_http you can use this instead...

"""

import time
import urllib2

from naglib.nagiosplugin import NagiosPlugin


class Any9Status(NagiosPlugin):
    VERSION = '1.1.0'

    def custom_options(self, parser):
        parser.add_option("-u", '--url', dest="url")

    def workload(self):
        if not self.options.url:
            self.exit_help('No url specified')
        if self.options.verbose > 1:
            print 'url: %s' % self.options.url
        t1 = time.time()
        issues = {}
        content = self.check_url(self.options.url)
        parts = content.split('<span class="name">')[1:]
        if not parts:
            self.exit_crit('%s does not look like a status page' % self.options.url)
        for s in parts:
            try:
                module = s.split('\n')[1].strip()
                status = s.split('<span class="component-status">')[1].split('</')[0].strip()
            except:
                self.exit_crit('Could not interperate output from: %s' % self.options.url)
            if status != 'Operational':
                if status not in issues:
                    issues[status] = []
                issues[status].append(module)
        t2 = time.time() - t1
        self.add_perf_data('response time', t2)
        if issues:
            bad_hosts = []
            for k in issues.keys():
                bad_hosts.append('%s: %s' % (k, ', '.join(issues[k])))
            msg = ', '.join(bad_hosts)
            self.exit_crit(msg)
        self.exit_ok('No issues reported')

    def check_url(self, url, timeout=10):
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
        return content


if __name__ == "__main__":
    Any9Status().run(standalone=True)

