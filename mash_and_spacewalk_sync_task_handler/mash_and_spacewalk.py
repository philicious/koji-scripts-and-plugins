# Koji Builder (kojid) plugin with two subtasks:
# 0. mash-and-spacewalk - main task 
# 1. mash		- mashes all packages tagged for testing repo
# 2. spacewalk		- syncs the newly mashed repo to spacewalk 
#
# Put it into /usr/lib/koji-builder-plugins
# Add line "plugins = mash_and_spacewalk" to /etc/kojid/kojid.conf and restart kojid
#
# Author:
#	Phil Schuler <the.cypher@gmail.com>
import koji
import koji.plugin
import koji.util
import koji.tasks
import logging
import logging.handlers
from koji.tasks import BaseTaskHandler
import subprocess
import xmlrpclib

SATELLITE_URL = "http://spacewalk.example.com/rpc/api"
SATELLITE_LOGIN = "admin"
SATELLITE_PASSWORD = "xkfoobar"
REPO_LABEL = 'foobar-testing-x86_64'

MASH_CONFIG_NAME = 'centos6-testing'

class MashAndSpacewalkTaskHandler(BaseTaskHandler):
    Methods = ['mash-and-spacewalk']

    def handler(self):
        task_id = self.session.host.subtask(method='mash',
                                            arglist=[],
                                            label='mash',
                                            parent=self.id)
        self.wait(task_id)

        task_id = self.session.host.subtask(method='spacewalk',
                                            arglist=[],
                                            label='spacewalk repo sync',
                                            parent=self.id)

        self.wait(task_id)        

        return
        
class MashTaskHandler(BaseTaskHandler):
    Methods = ['mash']

    def handler(self):
        command = "/usr/bin/mash -o /mnt/foobar/mash %s" % MASH_CONFIG_NAME
        child = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,shell=True)
        ret = child.wait()
        if ret != 0:
            raise koji.GenericError, "mash command (%s) failed: %s" % (command,child.communicate())
        elif ret == 0:
            logs = {}
            logs['mash.log'] = str(child.communicate())

            return logs

class SpacewalkTaskHandler(BaseTaskHandler):
    Methods = ['spacewalk']

    def handler(self):
        client = xmlrpclib.Server(SATELLITE_URL, verbose=0)
        key = client.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)

        res = client.channel.software.syncRepo(key,REPO_LABEL)

        client.auth.logout(key)
        if res != 1:
            raise koji.GenericError, "repo sync failed: %s" % res
        return "Repo Sync succeeded"
