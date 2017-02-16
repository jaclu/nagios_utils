#!/usr/bin/python
"""
 check_portal_rev.py for nagios
 Copyright 2014: europeana   License: EUPL
 Written by: Jacob.Lundqvist@europeana.eu
 jaclu 2014-04-07 vers 0.1.3

 Either just displays portal rev, or ensures specific version
"""


from naglib.nagiosplugin import NagiosPlugin


class CheckNaveRev(NagiosPlugin):
    VERSION = '0.1.0' # bad revision triggers warn instead of crit
    DESCRIPTION = "Displays portal version"
    CMD_LINE_HINT = 'host'
    ARGC = 1

    def custom_options(self, parser):
        parser.add_option("-r", "--rev", dest="nave_rev",
                          help="if specified specifies minimal accepted version")
        parser.add_option("-p", "--precise", dest="precise", action='store_true', default=False,
                          help="version must match exactly, otherwise minor rev can ")
        parser.add_option("-u", "--url", dest="url", default="/version")

    def do_rev_check(self, nave_vers):
        if self.options.precise:
            if self.options.nave_rev != nave_vers:
                self.exit_crit('Exact match requested, expected:%s found:%s' % (self.options.nave_rev, nave_vers))

        r_maj = '.'.join(nave_vers.split('.')[:2])
        r_min = nave_vers.split('.')[2]
        #
        # Parsing params
        #
        if len(self.options.nave_rev.split('.')) != 3:
            self.exit_crit('nave_rev should be in x.y.z format')
        p_maj = '.'.join(self.options.nave_rev.split('.')[:2])
        p_min = self.options.nave_rev.split('.')[2]

        if p_maj != r_maj:
            self.exit_crit('Major vers missmatcch, expected:%s found:%s' % (self.options.nave_rev, nave_vers))
        if p_min > r_min:
            self.exit_warn('Minor vers missmatcch, expected:%s found:%s' % (self.options.nave_rev, nave_vers))


    def workload(self):
        if len(self.args) != 1:
            self.exit_crit('Exactly one param expected! [%s]' % ' '.join(self.args))
        #
        # Parsing output
        #
        html = self.url_get(self.args[0], self.options.url)
        if html.find('nave_version') < 0:
            self.exit_crit('No portal revision data detected')
        parts = html.split('=')
        nave_vers = parts[1].split()[0]
        priv_vers = parts[2].split()[0]

        if self.options.nave_rev:
            self.do_rev_check(nave_vers)


        self.exit_ok('vers: %s  private: %s' % (nave_vers, priv_vers))


if __name__ == "__main__":
    CheckNaveRev().run(standalone=True)
