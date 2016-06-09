#!/usr/bin/env python
"""
If you cant install the nagios check_http you can use this instead...

"""

import sys
import time

try:
    import nmap
except:
    print('ERROR: Missing dependency, do: pip install python-nmap')
    sys.exit(1)


from naglib.nagiosplugin import NagiosPlugin


class CheckNmap(NagiosPlugin):
    VERSION = '0.1.1' # fixed closed port check
    CMD_LINE_HINT = 'hostname'

    def custom_options(self, parser):
        parser.add_option("-l", '--listening', dest="listening",
                            help='Ports expected to be open x x-y or x,y,z notation')
        parser.add_option("-c", '--closed', dest="closed",
                          help='Ports expected to be closed x x-y or x,y,z notation')

    def workload(self):
        if len(self.args) != 1:
            self.exit_help('Wrong number of params given')
        hostname = self.args[0]

        if (not self.options.listening) and (not self.options.closed):
            self.exit_crit('-l or -c must be specified')

        msg = []
        nm = nmap.PortScanner()

        t1 = time.time()

        bad_open = []
        if self.options.listening:
            nm.scan(hostname,arguments='-p %s' % self.options.listening)
            #nm.scan(hostname,arguments='-p %s' % self.options.blocked)
            ip = nm._scan_result['scan'].keys()[0]
            for port in nm[ip]['tcp'].keys():
                if nm[ip]['tcp'][port]['state'] != 'open':
                    bad_open.append(str(port))
        if bad_open:
            msg.append('should be open: %s' % ','.join(bad_open))

        bad_closed = []
        if self.options.closed:
            nm.scan(hostname,arguments='-p %s' % self.options.closed)
            #nm.scan(hostname,arguments='-p %s' % self.options.blocked)
            ip = nm._scan_result['scan'].keys()[0]
            for port in nm[ip]['tcp'].keys():
                if nm[ip]['tcp'][port]['state'] == 'open':
                    bad_closed.append(str(port))
        if bad_closed:
            msg.append('should be closed: %s' % ','.join(bad_closed))

        if msg:
            self.exit_crit(' '.join(msg))
        msg.append('Checks took %.2f seconds' % (time.time() - t1))
        msg.append('  PORTS:')
        if self.options.listening:
            msg.append('open: %s' % self.options.listening)
        if self.options.closed:
            msg.append('closed: %s' % self.options.closed)

        self.exit_ok(' '.join(msg))


if __name__ == "__main__":
    CheckNmap().run(standalone=True)

