#!/usr/bin/python

# simple version of check_http for nagios
# jaclu 2013-04-19 vers 1.0
# Im running this on a few production machines 
# where i cant install the nagios plugins

import urllib2
import sys

def check_url(url,s_expect):
    try:
    	f = urllib2.urlopen(url, timeout=10)
    except:
	f = urllib2.urlopen(url)
    if f.code != 200:
        print 'ERROR: %s %s' % (f.code, f.msg)
        sys.exit(2)
    content = f.read()
    if content.find(s_expect) < 0:
        print 'ERROR %s not found' % s_expect
        sys.exit(2)
    return
        
        
        
progname="./check_http.py "
url=sys.argv[1]
s_expect=sys.argv[2]
    
check_url(url,s_expect)
print 'OK - HTTP/1.1 200 OK'
