#!/usr/bin/python
#
# This script mashes the packages and calls Spacewalk to sync the repo.
#
# Author:
#	Phil Schuler <the.cypher@gmail.com>
#
#ensure apache can write to mash dir
# cd /mnt/foobar/mash
# rm -rf centos6-testing
# cd ..
# chgrp apache mash
# chmod g+w mash
#
#clean up old files owned by other users and set permissions
# cd /var/tmp/mash/
# rm -rf mash-centos6-testing
# cd ..
# chgrp apache mash
# chmod g+w mash
# cd /var/cache/mash
# rmdir *

import xmlrpclib
import subprocess
import logging
import sys

### Spacewalk config ###
SATELLITE_URL = "http://spacewalk.example.net/rpc/api"
SATELLITE_LOGIN = "admin"
SATELLITE_PASSWORD = "xKfoobar"
REPO_LABEL = 'foobar-testing-x86_64'

### mash config ###
MASH_CONFIG_NAME = 'centos6-testing'

def spacewalk_sync():
    client = xmlrpclib.Server(SATELLITE_URL, verbose=0)
    key = client.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)

    res = client.channel.software.syncRepo(key,REPO_LABEL)
    logging.info('Spacewalk sync returned with status: %s',res)
    
    client.auth.logout(key)    
    if res != 1:
        logging.error('Spacewalk sync failed: %s',res)

def mash_repo(tag):
    command = "/usr/bin/mash -o /mnt/foobar/mash %s" % tag
    child = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,shell=True)
    ret = child.wait()
    logging.info('mash returned with code: %s',ret)
    if ret != 0:
        logging.error('mash command failed: %s returned: %s',command,child.communicate())
        sys.exit(1)
    elif ret == 0:
        logging.info('mash output: %s',child.communicate())
        spacewalk_sync()

mash_repo(MASH_CONFIG_NAME)
