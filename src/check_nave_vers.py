#!/usr/bin/python
"""
 check_portal_rev.py for nagios
 Copyright 2017:   License: GPL
 Written by: Jacob.Lundqvist@gmail.com
 jaclu 2017-02-21 vers 0.1.1

"""


from naglib.nagiosplugin import NagiosPlugin


class CheckNaveRev(NagiosPlugin):
    VERSION = '0.1.1'
    DESCRIPTION = "Displays nave version"
    CMD_LINE_HINT = 'host'
    ARGC = 1

    def custom_options(self, parser):
        parser.add_option("-r", "--rev", dest="nave_rev",
                          help="if specified specifies minimal accepted version")
        parser.add_option("-l", "--lax", dest="relaxed", action='store_true', default=False,
                          help="minor mismatch does not trigger WARN")
        parser.add_option("-p", "--precise", dest="precise", action='store_true', default=False,
                          help="version must match exactly")
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
        # get rid of non numeric prefix
        while self.options.nave_rev[0] not in '1234567890':
            self.options.nave_rev = self.options.nave_rev[1:]
        parts = self.options.nave_rev.split('.')
        for p in parts:
            try:
                int(p)
            except:
                msg = 'Non integer part in version number: %s' % p
                self.exit_crit(msg)
        p_maj = '.'.join(parts[:2])
        p_min = '.'.join(parts[2:])

        if p_maj != r_maj:
            self.exit_crit('Major vers missmatcch, expected:%s found:%s' % (self.options.nave_rev, nave_vers))
        if p_min > r_min:
            msg = 'Minor vers missmatcch, expected:%s found:%s' % (self.options.nave_rev, nave_vers)
            if self.options.relaxed:
                self.exit_ok(msg)
            else:
                self.exit_warn(msg)


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
