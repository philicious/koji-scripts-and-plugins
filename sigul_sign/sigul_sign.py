# Koji-Plugin to auto-sign built packages with sigul
#
# Put into /usr/lib/koji-hub-plugins and enable in /etc/koji-hub/hub.conf
#
# You need to add apache to sigul group and chmod -R g=rw /var/lib/sigul;chmod g=rwx /var/lib/sigul,
# otherwise the plugin cant execute the sigul command.
#
# The plugin is run as kojid user so that user needs permissions for signing packages:
# su kojiadmin; koji grant-permission admin kojid
#
# Version: 0.1
#
# Authors:
# 		Phil Schuler <the.cypher@gmail.com>

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
passphrase = 'for-your-gpg-key'
gpg_key_name = 'foobar'
gpg_key_id = '6174aaaa'
build_target = 'dist-centos6'
testing_tag = 'dist-centos6-testing'

def sigul_sign(cbtype, *args, **kws):
    # make sure its a package build and not a re-tag or sth
    if kws['tag']['name'] != build_target:
    	return
    	
    # make sure the build succeeded
    if kws['build']['state'] != 1:
        logging.getLogger('koji.plugin.sigul_sign').error('build state not finished')
        return
    
    logging.getLogger('koji.plugin.sigul_sign').info('buildinfo: %s',str(kws))
    
    # find all rpms for this build
    kojifunctions = RootExports()
    build_rpms = kojifunctions.listBuildRPMs(kws['build']['id'])
    logging.getLogger('koji.plugin.sigul_sign').info('rpminfo: %s',str(build_rpms))

    # finally sign and write rpms to disk
    for rpm_info in build_rpms:
        rpm_name = "%s.%s" % (rpm_info['nvr'],rpm_info['arch'])
        sigul_sign_rpm(rpm_name)
       	kojifunctions.writeSignedRPM(rpm_name,gpg_key_id)    

    # and tag it for testing-repo
    kojifunctions.tagBuild(testing_tag,kws['build']['id'])
    logging.getLogger('koji.plugin.sigul_sign').info('package %s was tagged to %s'%(kws['build']['name'],testing_tag))

def run_sigul(command):
    child = subprocess.Popen(command, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,shell=True)
    child.stdin.write(passphrase + '\0')
    ret = child.wait()
    logging.getLogger('koji.plugin.sigul_sign').info('sigul returned with code: %s',ret)
    if ret != 0:
        logging.getLogger('koji.plugin.sigul_sign').error('sigul command failed: %s returned: %s',command,child.communicate())
        sys.exit(1)

def sigul_sign_rpm(rpm_name):
    # make sure the key is working
    command = "sigul --batch get-public-key %s" % gpg_key_name
    run_sigul(command)

    # run the actual sign/import command
    command = "sigul --batch sign-rpm --koji-only --store-in-koji --v3-signature %s %s" % (gpg_key_name, rpm_name)
    logging.getLogger('koji.plugin.sigul_sign').info('running sigul command: %s',command)    
    run_sigul(command)

register_callback('postTag',sigul_sign)
