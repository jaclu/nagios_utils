#!/usr/bin/python

# check_postgres.py for nagios
# Copyright 2014: europeana.eu   License: EUPL
# Written by: Jacob.Lundqvist@europeana.eu
# version info - see CheckPostgres header

#  -U thumblr -P sdkhjkh54df -d thumblr2 -Q 'select count(*) from plug_uris_uri' -c 'x > 10'

from naglib.nagiosplugin import NagiosPlugin


def cmd_strip_password(cmd):
    if cmd.find('PGPASSWORD') < 0:
        return cmd  # pw not used
    # strip until first whitespace'
    parts = cmd.split()
    r = 'PGPASSWORD=xxxxxxx ' + ' '.join(parts[1:])
    return r

# TODO write unittests
class CheckPostgres(NagiosPlugin):
    VERSION = '0.3.6'
    HELP = """
    -c --condition   Boolean examining the output of the query, to end up in a True/False state
       example:
           'x > 10'    query result must be larger than 10


"""
    CMD_LINE_HINT = 'filepath'
    ARGC = '*'  # * = 0 or larger, n = exact match, 2+ two or more, 1-3 one to three

    def custom_options(self, parser):
        parser.add_option("-l", '--listdb', action="store_true", dest="listdb", default=False,
                          help='request a listing of all databases')
        parser.add_option('-d', '--database', dest='database',
                          help='investigate a specific database')
        parser.add_option('-U', '--username', dest='username',
                          help='Authentication (optional)')
        parser.add_option('-p', '--password', dest='password',
                          help='Authentication (optional)')

        parser.add_option('-H', '--host', dest='host', help='hostname')

        parser.add_option('-Q', '--query', dest='query')

        parser.add_option('-c', '--condition', dest='condition',
                          help='boolean condition done upon output of query')
        parser.add_option('-L', '--label', dest='label',
                          help='Give a label for the output in order to be able to use Nagios Performance data')

    def workload(self):
        if self.options.listdb:
            self.listdb()
        if not self.options.database:
            self.exit_crit('No database specified')
        if not self.options.query:
            self.exit_crit('No query specified')
        self.run_query(self.options.query)
        self.exit_ok('test condition true')

    def run_query(self, q):
        cmd = self.build_cmd(q)
        retcode, stdout, stderr = self.cmd_execute_output(cmd)
        if retcode:
            self.exit_crit('cmd failed: %s' % cmd_strip_password(cmd))
        r = stdout.strip()
        if self.options.label:
            label = self.options.label
            if label.find(' ') > -1:
                self.exit_crit('label param can not contain white space(%s)' % label)
            result_msg = '%s=%s' % (label, r)
        else:
            result_msg = r
        condition = self.options.condition
        if not condition:
            self.exit_ok(result_msg)

        parts = condition.split('x')
        if len(parts) < 2:
            self.exit_crit('invalid boolean condition (%s), use "x" for the data your comparing' % condition)

        c2 = []
        for part in parts:
            if part:
                c2.append(part)
            else:
                c2.append(r)
        sql = ''.join(c2)

        cmd = self.build_cmd('SELECT %s' % sql)
        retcode, stdout, stderr = self.cmd_execute_output(cmd)
        if retcode:
            self.exit_crit('cmd failed: %s' % cmd_strip_password(cmd))
        if stdout.strip().lower() != 't':
            self.exit_crit('condition returned false: %s' % sql)
        self.exit_ok(result_msg)

    def build_cmd(self, sql):
        if sql[-1] != ';':
            sql += ';'

        cmd = 'psql'
        if self.options.database:
            cmd += ' -d %s' % self.options.database
        if self.options.username:
            cmd += ' -U %s' % self.options.username
        if self.options.host:
            cmd += ' -h %s' % self.options.host
        if self.options.password:
            cmd = 'PGPASSWORD=%s %s' % (self.options.password, cmd)
        cmd += ' -t -c "%s"' % sql
        return cmd

    def listdb(self):
        db = self.options.database
        self.options.database = ''
        cmd = self.build_cmd('SELECT datname FROM pg_database WHERE datistemplate = false')
        # cmd = 'psql -t -U postgres -c "SELECT datname FROM pg_database WHERE datistemplate = false;"'
        retcode, stdout, stderr = self.cmd_execute_output(cmd)
        if retcode:
            self.exit_crit('Command failed (%i): %s' % (retcode, cmd_strip_password(cmd)))

        databases = stdout.split()
        if db:
            if db in databases:
                self.exit_ok('database %s is present' % db)
            else:
                self.exit_crit('database %s missing' % db)

        self.exit_ok('databases: %s' % ' '.join(stdout.split()))


if __name__ == "__main__":
    CheckPostgres().run(standalone=True)
