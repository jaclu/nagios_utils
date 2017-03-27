#!/usr/bin/env python
"""
If you cant install the nagios check_http you can use this instead...

"""

import time

from naglib.nagiosplugin import NagiosPlugin


class CheckElasticStatus(NagiosPlugin):
    VERSION = '0.5.0'
    DESCRIPTION = "Checks status of elastic cluster (green/yellow/red)"

    def custom_options(self, parser):
        parser.add_option('-H', '--host', dest="host", default='localhost',help='defaults to %default')
        parser.add_option('-p', '--port', dest="port", type='int', default='9200',help='defaults to %default')
        parser.add_option('-u', '--url', dest="url", default='/_cluster/health',help='defaults to %default')

    def workload(self):
        if not self.options.host:
            self.exit_crit('No host specified')
        if not self.options.port:
            self.exit_crit('No port specified')
        if not self.options.url:
            self.exit_crit('No url specified')

        # First ensure server is running properly
        url1 = '%s:%i' % (self.options.host, self.options.port)
        try:
            html = self.url_get(url1,own_handling_status_error=True)
        except:
            self.exit_crit('Cluster not operational: %s' % url1)

        url2 = '%s:%i%s' % (self.options.host, self.options.port, self.options.url)
        html = self.url_get(url2)
        try:
            parts = html.split('"status":"')
            stat = parts[1].split('"')[0]
        except:
            stat = 'status not found in output'
        if stat == 'green':
            self.exit_ok('status is green')
        elif stat =='yellow':
            self.exit_warn('status is yellow')
        self.exit_crit('status is %s' % stat)


if __name__ == "__main__":
    CheckElasticStatus().run(standalone=True)

