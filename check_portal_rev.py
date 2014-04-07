#!/usr/bin/python
"""
 check_portal_rev for nagios 
 Copyright 2014: europeana   License: EUPL
 Written by: Jacob.Lundqvist@europeana.eu
 jaclu 2014-04-07 vers 0.1.0
 
 Either just displays portal rev, or ensures specific version
"""

from optparse import OptionParser
import subprocess
import sys




class PortalRev(object):
    
    def __init__(self):
        self.cmd_line()
        
    def run(self):
        cmd = 'curl %s/portal/build.txt' % (self.server)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, close_fds=True)
        output = p.stdout.readlines()
        p.communicate()
        retcode = p.returncode
        if retcode:
            print 'ERROR: Command failed (%i): %s' % (retcode, cmd)
            sys.exit(2)
            
        parts = output[0].split()
        
        rev = parts[1]
        build_time = parts[4] + ' ' + parts[5]
        version = parts[-1][:-1]
        
        if self.options.revision:
            if rev != self.options.revision:
                print 'ERROR: Revision: %s (expected: %s)' % (rev, self.options.revision)
                sys.exit(2)
            
        if self.options.build_time:
            if build_time.find(self.options.build_time) < 0:
                print 'ERROR: Build: %s (expected: %s)' % (build_time, self.options.build_time)
                sys.exit(2)
                
        if self.options.vers:
            if version != self.options.vers:
                print 'ERROR: Version: %s (expected: %s)' % (version, self.options.vers)
                sys.exit(2)
                    
        print 'OK: vers:%s rev:%s build:%s' % (version, rev, build_time)
        


    def cmd_line(self):
        parser = OptionParser()
        usage = "usage: %prog [options] arg1 arg2"
        parser.add_option("-r", "--revision", 
                          #action="store_true", default=False, 
                          dest="revision")
        parser.add_option("-v", "--vers", 
                          #action="store_true", default=False, 
                          dest="vers")
        parser.add_option("-b", "--build_time", 
                          #action="store_true", default=False, 
                          dest="build_time")
        self.options, self.arguments = parser.parse_args()
        
        if not len(self.arguments) == 1:
            print
            print 'Server must be given'
            sys.exit(1)
        self.server = self.arguments[0]


pr = PortalRev()
pr.run()