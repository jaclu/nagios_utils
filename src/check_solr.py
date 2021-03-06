#!/usr/bin/env python


import time
import urllib2
import httplib
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse

from naglib.nagiosplugin import NagiosPlugin


# TODO write unittests
class CheckSolr(NagiosPlugin):
    VERSION = '1.1.4'
    DEFAULT_REL_URL = '/solr/search/select?q=*:*&rows=0'
    #DEFAULT_REL_URL = '/solr/search_1/select?q=*:*&rows=0'
    CMD_LINE_HINT = 'url'
    HELP = """
    if only http://adr[:port] is used as url

       %s

    will be appended.

    """ % DEFAULT_REL_URL

    def custom_options(self, parser):
        parser.add_option("-c", '--count', dest="count", type='int', default=0,
                          help='check number of items in DB')
        parser.add_option("-r", '--running', action="store_true", dest="running", default=False,
                          help='Verify that this is a running solr')

    def workload(self):
        if len(self.args) != 1:
            self.exit_help('Mandatory param missing')
        url = self.args[0]

        if self.options.count and self.options.running:
            self.exit_crit('Only one of -c / -r can be given')
        if not (self.options.count or self.options.running):
            self.exit_crit('Either one of -c / -r must be given')

        o = urlparse(url)
        if not o.path:
            url += self.DEFAULT_REL_URL

        if self.options.verbose > 1:
            print 'url: %s' % url
            if self.options.count:
                print 'expected item count: %i' % self.options.count  # TODO count isnt defined

        t1 = time.time()
        content = self.check_url(url)
        t2 = time.time() - t1
        self.add_perf_data('response time', t2)

        if self.options.count:
            self.check_count(content)

        #
        # basic check that server seems to be a solr
        #
        if content.find('numFound="') == -1:
            self.exit_crit('No solr service found')
        self.exit_ok('Solr responsive')

    def check_url(self, url, timeout=10):
        t1 = time.time()
        try:
            f = urllib2.urlopen(url, timeout=timeout)
        except urllib2.HTTPError, e:
            self.exit_crit('HTTP error:%i - %s' % (e.code, e.msg))
        except urllib2.URLError, e:
            self.exit_crit('URL error: %s' % e.reason)
        except httplib.BadStatusLine, e:
            if not e.line == 3:
                self.exit_crit('No response - server down?')
            else:
                self.exit_crit('Unknown error: %s' % e)
        except:
            if time.time() > t1 + timeout:
                self.exit_crit('timeout')
            self.exit_crit('unknwon failure processing url - maybe not responding?')
        if f.code != 200:
            self.exit_crit('Bad response: %s %s' % (f.code, f.msg))
        content = f.read()
        return content

    def check_count(self, content):
        parts = content.split('numFound="')
        if len(parts) < 2:
            self.exit_crit('numFound not found in output')
        try:
            actual_count = int(parts[1].split('"')[0])
        except:
            self.exit_crit('numFound found but no itemcount')

        if self.options.count != actual_count:
            self.exit_crit('Expected %i items, found %i - diff %i' % (self.options.count, actual_count,
                                                                      actual_count - self.options.count))
        self.exit_ok('Itemcount as expected: %i' % self.options.count)


if __name__ == "__main__":
    CheckSolr().run(standalone=True)

