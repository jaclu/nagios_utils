#!/usr/bin/python
"""
 check_portal_rev.py for nagios
 Copyright 2014: europeana   License: EUPL
 Written by: Jacob.Lundqvist@europeana.eu
 jaclu 2014-04-07 vers 0.1.3

 Either just displays portal rev, or ensures specific version
"""


from naglib.nagiosplugin import NagiosPlugin


class CheckPortalRev(NagiosPlugin):
    VERSION = '1.1.1' # bad revision triggers warn instead of crit
    DESCRIPTION = "Displays portal version"
    CMD_LINE_HINT = 'host'
    ARGC = 1

    def custom_options(self, parser):
        parser.add_option("-r", "--revision", dest="revision")
        parser.add_option("-V", "--vers", dest="vers")
        parser.add_option("-b", "--build_time", dest="build_time")
        parser.add_option("-u", "--url", dest="url", default="/portal/build.txt")

    def workload(self):
        if len(self.args) != 1:
            self.exit_crit('Exactly one param expected! [%s]' % ' '.join(self.args))

        html = self.url_get(self.args[0], self.options.url)
        parts = html.split()

        if parts[0] != 'Revision':
            self.exit_warn('No portal revision data detected')
        rev = parts[1]
        build_time = parts[4] + '_' + parts[5]
        version = parts[-3][:-1]
        branch = parts[-1].replace(')', '')

        if self.options.revision:
            if rev != self.options.revision:
                self.exit_warn('Revision: %s (expected: %s)' % (rev, self.options.revision))

        if self.options.build_time:
            if build_time.find(self.options.build_time) < 0:
                self.exit_crit('Build: %s (expected: %s)' % (build_time, self.options.build_time))

        if self.options.vers:
            if version != self.options.vers:
                self.exit_crit('Version: %s (expected: %s)' % (version, self.options.vers))

        self.exit_ok('vers:%s branch:%s rev:%s build:%s' % (version, branch, rev, build_time))


if __name__ == "__main__":
    CheckPortalRev().run(standalone=True)
