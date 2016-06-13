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
    VERSION = '0.1.4' # added speedup options
    CMD_LINE_HINT = 'hostname'
    COMMON_NMAP_OPTIONS = '-T5 -n --max-retries 0'

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

        not_open = []
        if self.options.listening:
            nm.scan(hostname,arguments='%s -p %s' % (self.COMMON_NMAP_OPTIONS,options.listening))
            if int(nm._scan_result['nmap']['scanstats']['downhosts']):
                self.exit_crit('Host seems down')
            #nm.scan(hostname,arguments='-p %s' % self.options.blocked)
            ip = nm._scan_result['scan'].keys()[0]
            for port in nm[ip]['tcp'].keys():
                if nm[ip]['tcp'][port]['state'] != 'open':
                    not_open.append(str(port))
        if not_open:
            not_open.sort()
            msg.append('should be open: %s' % ','.join(not_open))

        not_closed = []
        if self.options.closed:
            nm.scan(hostname,arguments='%s -p %s' % (self.COMMON_NMAP_OPTIONS,self.options.closed))
            if int(nm._scan_result['nmap']['scanstats']['downhosts']):
                self.exit_crit('Host seems down')
            #nm.scan(hostname,arguments='-p %s' % self.options.blocked)
            ip = nm._scan_result['scan'].keys()[0]
            for port in nm[ip]['tcp'].keys():
                if nm[ip]['tcp'][port]['state'] == 'open':
                    not_closed.append(str(port))
        if not_closed:
            not_closed.sort()
            msg.append('should be closed: %s' % ','.join(not_closed))

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

