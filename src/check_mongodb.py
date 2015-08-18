#!/usr/bin/env python


import tempfile

from naglib.nagiosplugin import NagiosPlugin


# TODO write unittests
class CheckMongoDb(NagiosPlugin):
    VERSION = '1.2.1'
    DESCRIPTION = "Warns if back-log of thumblr2 files is to large, or oldest file waiting is to old"
    CMD_LINE_HINT = 'database collection/special_query [filter]'
    HELP = """
    If second param contains no dot (.) it is assumed to be a collection
    and test will succeed if this collection has more than zero records.

    If there is a dot this is assumed to be a full query and it will be run as given
      example: db.record.findOne()

    If a filter option is given, this is piped in after the mongodb call, useful for a grep or regexp
        in combination with a special query to verify specific content is available
        it is assumed a post_cmd will generate output if successful
        empty result is assumed to be a failed test
    """

    def custom_options(self, parser):
        parser.add_option("-u", '--username', dest="username", default='')
        parser.add_option("-p", '--password', dest="password", default='')
        parser.add_option("-f", '--filter', dest="filter", default='')
        parser.add_option("-m", '--mongo', dest="mongo_cmd", default='mongo')

    def workload(self):
        if len(self.args) < 2:
            self.exit_help('Mandatory param missing')
        database = self.args[0]
        query = self.args[1]

        is_record_count = False
        if query.find('.') == -1:
            is_record_count = True
            query = 'db.%s.count()' % query

        f = tempfile.NamedTemporaryFile(prefix="check_mongodb.py-")
        auth = self.auth_me()
        if auth:
            f.write('use admin\n')
            f.write('%s\n' % auth)
        f.write('use %s\n' % database)
        f.write('%s\n' % query)

        f.flush()
        print f.name
        cmd = 'cat "%s"|%s --quiet' % (f.name, self.options.mongo_cmd)

        if self.options.filter:
            cmd += ' | %s' % self.options.filter
        retcode, stdout, stderr = self.cmd_execute_output(cmd)
        f.close()
        if stderr:
            self.exit_crit(stderr)
        elif retcode == 1 and stdout == '':
            #
            if cmd.find('grep') > -1:
                self.exit_crit('grep did not find a match: %s' % self.options.filter)
            self.exit_crit('cmd failed, no output received')
        elif retcode:
            self.exit_crit('cmd failed %s' % stdout)

        if self.options.filter:
            output = stdout.strip()
        else:
            output = '\n'.join(stdout.split('\n')[3:]).strip()
        if is_record_count:
            try:
                msg = 'Found %i items' % int(output)
            except:
                self.exit_crit(output)
        elif self.options.filter and stdout:
            msg = 'post filter matched'
        else:
            self.exit_crit('Other error')

        self.exit_ok(msg)

    def auth_me(self):
        if self.options.username == '' and self.options.password == '':
            return ''
        return "db.auth('%s','%s')" % (self.options.username, self.options.password)


if __name__ == "__main__":
    CheckMongoDb().run(standalone=True)

"""
arg_count = len (sys.argv) - 1

if not arg_count:
    print
    print 'check_mongodb.py database collection/special_query [post_cmd]'
    print
    print '\tFor remote databases use hostname:port/database notation'
    print
    print '\tIf second param contains no dot (.) it is assumed to be a collection'
    print '\t and test will succeed if this collection has more than zero records.'
    print
    print '\tIf there is a dot this is assumed to be a full query and it will be run as given'
    print '\t example: db.record.findOne()'
    print
    print '\tIf a post_cmd is given, this is piped in after the mongo call, usefull for a grep or regexp'
    print '\t in combination with a special query to verify specific content is available'
    print '\t it is assumed a post_cmd will generate output if successfull'
    print '\t empty result is assumed to be a failed test'
    print
    sys.exit(2)

try:
    db = sys.argv[1]
except:
    print 'ERROR: first param must be a database name'
    sys.exit(2)

try:
    collection = sys.argv[2]
    if collection.find('.') > -1:
        s_input = collection
    else:
        s_input = 'db.%s.count()' % collection
except:
    print 'ERROR: second param must be a collection name'
    sys.exit(2)

post_cmd = ''
if arg_count > 2:
    post_cmd = '| %s' % sys.argv[3]

cmd = 'echo "%s" | mongo --quiet %s %s' % (s_input, db, post_cmd)
if DEBUG:
    print '*** Cmd that will be run on next line'
    print cmd
    print
p = subprocess.Popen(cmd,
                     shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
output = p.stdout.readlines()
p.communicate()
retcode = p.returncode

if retcode:
    print 'ERROR: Command failed (%i): %s' % (retcode, cmd)
    sys.exit(2)

if post_cmd:
    if isinstance(output, list):
        #print '*** it was a list'
        s = ' '.join(output)
        #print 'pre strip {{%s}}' % s
        output = s.strip()
        #print 'post strip {{%s}}' % output

    if output:
        print 'OK - extended test successful'
        sys.exit(0)
    else:
        print 'ERROR: Extended test failed!'
        sys.exit(2)

#
# assuming it was a record count
#2
try:
    # old mongoclient test
    count = int(output[-2])
except:
    if DEBUG:
        print '** Old style count parsing failed'
    try:
        # starting at vers 2.6.7 this works
        count = int(output[0].strip())
    except:
        print 'ERROR: Failed to read record count: %s' % output
        sys.exit(2)
if not count:
    print 'ERROR: zero records found, did you use correct DB name?'
    sys.exit(2)
print 'OK - %i records' % count
"""