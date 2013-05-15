# Koji plugin for starting mash in background after a build
# got tagged for mashing.
# Make sure that user apache can call 'python /path/to/mash_spacewalk.py'
#
# Authors:
#       Phil Schuler <the.cypher@gmail.com>

import koji
from koji.plugin import register_callback, ignore_error
import sys
if not "/usr/share/koji-hub" in sys.path:
    sys.path.append("/usr/share/koji-hub")
import kojihub
from kojihub import RootExports
import logging
import subprocess
import time

# this should come from config file
testing_tag = 'dist-centos6-testing'

def mash_repo(cbtype, *args, **kws):
    if kws['tag']['name'] != testing_tag:
        return
    child = subprocess.Popen('python /opt/foobar/mash_and_spacewalk/mash_and_spacewalk.py',shell=True).pid
    logging.getLogger('koji.plugin.mash').info('started mash with pid: %s',child)

register_callback('postTag',mash_repo)
