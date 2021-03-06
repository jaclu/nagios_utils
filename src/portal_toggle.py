#!/usr/bin/python

"""
This isnt really a nagios plugin, but since it calls one, I re-use some code
and put it hear for convenience.

The actual switchover depends on an external binary - '~/bin/activate-environ
if that is not found, nothing bad happens, only scaling up of the passive side
"""

import time

from check_cf_app import CheckCfApp
from naglib.nagiosplugin import NagiosPlugin

TASK_LIST = 'list'
TASK_TOGGLE = 'toggle'
VERBS = (TASK_LIST, TASK_TOGGLE)


# TODO write unittests
class PortalToggler(NagiosPlugin):
    VERSION = '2.2.0'  # added -n toggle
    DESCRIPTION = "lists/toggles production portal"
    CMD_LINE_HINT = 'list / toggle'
    HELP = """
    list          show what app is currently handling production
    toggle        switches to other app after first
                   * ensuring its running
                   * ensuring the correct number of instances are running
                   * all apps are responsive
                  after switch
                   * restarts retired group
                   * scales all retired apps down to 1 instance

    """
    APP_WEB = 'web'
    APP_API = 'api'
    APP_PORTAL = 'portal'
    APP_BOTTER = 'botter'
    APPS = (APP_BOTTER, APP_PORTAL, APP_API, APP_WEB)
    INSTANCES = {APP_BOTTER: 3, APP_PORTAL: 3, APP_API: 3, APP_WEB: 2}  # this also defines the scale - # instances
    GROUPS = ('blue', 'green')

    PROC_TIMEOUT = 900

    def custom_options(self, parser):
        parser.add_option("-C", '--command', dest='command', default='cf')
        parser.add_option('-P', '--prefix', dest='plugin_prefix', default='/usr/local/nagiosplugins')
        parser.add_option("-n", '--no_scaledown', dest="no_scaledown", action="store_true", default=False,
                          help='Dont scale down the retiring environ')

    def workload(self):
        if len(self.args) != 1:
            self.exit_crit('exactly one task must be suplied as param')
        task = self.args.pop()
        if task not in VERBS:
            self.exit_crit('invalid task: %s' % task)

        initially_active, initially_passive = self.task_list()  # check what stack is currently active
        msg = 'Currently %s is active' % initially_active
        if task == TASK_LIST:
            self.exit_ok(msg)
        self.log(msg, 1)
        #
        # Activate the incoming group
        #
        self.activate_stack(group=initially_passive, startup=True)
        #
        # Do the actual switchover
        #
        self.log('will now toggle production to %s' % initially_passive, 1)
        cmd = '~/bin/activate-environ %s' % initially_passive
        self.cmd_execute_abort_on_error(cmd, self.PROC_TIMEOUT)
        #
        # Retire the inactive group
        #
        if not self.options.no_scaledown:
            self.activate_stack(group=initially_active, startup=False)
        else:
            self.log('Not scaling down %s' % initially_active)

        open('/tmp/portal_toggle.log', 'a').write('%s - activated: %s\n' % (time.asctime(), initially_passive))
        self.exit_ok('portal toggled sccessfully, %s is now active' % initially_passive)

    def task_list(self):
        # check what stack is currently active
        cmd = '%s routes' % self.options.command
        self.log('Checking routes', 2)
        stdout = self.cmd_execute_abort_on_error(cmd)
        for line in stdout.split('\n'):
            if line.find('www') > -1 and line.find('europeana.eu') > -1:
                active = line.split()[-1].split('-')[0]
                break

        if active not in self.GROUPS:
            self.exit_crit('active group (%s) not recognized' % active)

        if active == 'blue':
            passive = 'green'
        else:
            passive = 'blue'
        return active, passive

    def activate_stack(self, group, startup=True):
        """For startup True, all apps are scaled to production level
        and then the app is started if not allready running
        For startup=False all apps are scaled to 1 and restarted
        Finally we wait for all apps to be ready and operational before
        returning, upon successfull return, groups can be toggled.
        """
        if startup:
            msg = 'Preparing'
        else:
            msg = 'Retiring'
        self.log('%s stack %s' % (msg, group), 1)

        for app in self.APPS:
            app_name = '%s-%s' % (group, app)
            if startup:
                scale = self.INSTANCES[app]
            else:
                scale = 2
            self.log('    scaling %s to %i instances and restarting' % (app_name, scale), 2)
            self.scale_app(app_name, scale)
            cmd = '%s restart %s' % (self.options.command, app_name)
            self.cmd_execute_abort_on_error(cmd, self.PROC_TIMEOUT)

        if startup:
            final_status = 'active'
            self.log('  Waiting for all apps to beceome ready', 1)
            time.sleep(10)  # give apps some time to start their processing
            timeout = time.time() + 900
            while True:
                all_ok = True
                for app in self.APPS:
                    app_name = '%s-%s' % (group, app)
                    self.log('\tchecking %s' % app_name, 2)
                    param_args = [app_name, '-I', '%s' % scale]
                    if self.options.plugin_prefix:
                        extra_opt = ['--command', self.options.command]
                        if param_args:
                            param_args += extra_opt
                        else:
                            param_args = extra_opt
                    CheckCfApp(param_args).run()
                    #  cmd = '%s/check_cf_app.py %s -I %i' % (self.options.plugin_prefix, app_name, scale)
                    # try:
                    #    b = self.cmd_execute_raise_on_error(cmd, self.PROC_TIMEOUT)
                    # except:
                    #    all_ok = False
                    #    break
                if all_ok:
                    break
                if time.time() > timeout:
                    self.exit_crit('Timeout waiting for one of the apps to come online')
                self.log('    Waiting max %is before timeout' % int(timeout - time.time()), 1)
                time.sleep(10)
        else:
            final_status = 'suspended'
        self.log('  %s is now %s' % (group, final_status), 1)
        return

    def scale_app(self, app_name, count):
        cmd = '%s scale -i %i %s' % (self.options.command, count, app_name)
        self.cmd_execute_abort_on_error(cmd, self.PROC_TIMEOUT)

    def app_is_running(self, app_name):
        cmd = '%s app %s' % (self.options.command, app_name)
        stdout = self.cmd_execute_abort_on_error(cmd, self.PROC_TIMEOUT)
        if stdout.find('requested state: started') > -1:
            running = True
            msg = 'is'
        else:
            running = False
            msg = 'is not'
        self.log('\t%s is %s running' % (app_name, msg), 3)
        return running


if __name__ == "__main__":
    PortalToggler().run(standalone=True)
