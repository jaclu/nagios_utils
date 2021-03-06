#!/usr/bin/python

"""
  Simple nagios style deb-checker
  version: 0.2.0
  last changed: 2013-11-11
  by: Jacob.Lundqvist@gmail.com
  copyright: 2013  Europeana.eu license: EUPL
"""

import os
import sys
from subprocess import Popen, PIPE

# TODO write unittests

nag_check_cmd = '/usr/lib/nagios/plugins/check_apt'


if not os.path.exists(nag_check_cmd):
    print 'CRITICAL: external cmd missong: %s' % nag_check_cmd
    print 'usually found in pkg: nagios-plugins-basic'
    sys.exit(2)

try:
    a = Popen(nag_check_cmd, stdout=PIPE)
    a.wait()
    line = a.stdout.readline().strip()
    relevant_line = line.split(':')[1].strip()
    crits = relevant_line.split('(')[1].split('(')[0][:-2]
    crit_count = int(crits.split()[0])
    reg_count = int(relevant_line.split()[0])
except:
    print 'cmd failed'
    sys.exit(2)

if crit_count:
    print '%s' % crits
    sys.exit(1)

if 0:  # reg_count:
    print '%s' % relevant_line
    sys.exit(1)
    
print '%s' % relevant_line
