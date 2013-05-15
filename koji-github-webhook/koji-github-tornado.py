#!/usr/bin/python
#
# A listener for Github webhook. It will trigger koji builds on commits with message containing #kojibuild
# You can also scratch build with #kojibuild #scratch in the commit message.
# Your repo should have one folder per package and inside version-folders. Then the spec + Makefile, e.g.:
# nginx/1.2.6/
#            \_ nginx-1.2.6.spec
#            |_ Makefile
# That layout will tell koji to use /github_username/reponame.git?nginx/1.2.6/#HEAD for the build.
# You also need to add an SSH key to your root user if the repo is private.
#
# Author:
#	Phil Schuler <the.cypher@gmail.com>
import tornado.ioloop
import tornado.web
import json
import re
import koji
import os

BUILD_SCRATCH_FLAG = '#scratch'
BUILD_TRIGGER = '#kojibuild'
KOJIHUB = 'https://koji.example.com/kojihub'
SERVERCA = os.path.expanduser('/home/kojiadmin/.koji/serverca.crt')
CLIENTCA = os.path.expanduser('/home/kojiadmin/.koji/clientca.crt')
CLIENTCERT = os.path.expanduser('/home/kojiadmin/.koji/client.crt')
BUILD_TARGET = 'dist-centos6'

class MainHandler(tornado.web.RequestHandler):
    def koji_build(self,url,opts):
        kojisession = koji.ClientSession(KOJIHUB)
        kojisession.ssl_login(CLIENTCERT, CLIENTCA, SERVERCA)
        result = kojisession.build(url,BUILD_TARGET,opts)
        print result

    def post(self):
        payload = json.loads(self.get_argument('payload'))
        
        # parse out what we need
        commits = payload['head_commit']['modified']
        commits.extend(payload['head_commit']['added'])    
        commit_message = payload['head_commit']['message']
        repo_url = payload['repository']['url']
        revision = payload['after']                
        
    	if BUILD_TRIGGER in commit_message:
            repo_path = commits[0].split('/')
            repo_path = "%s/%s/#%s" % (repo_path[0],repo_path[1],revision)
       	    repo_url = re.sub(r'^https?://','git+ssh://git@',repo_url)
       	    repo_url = "%s.git?%s" % (repo_url,repo_path)

            opts = {'scratch':0}
       	    if BUILD_SCRATCH_FLAG in commit_message:
                opts['scratch'] = 1
            
            self.koji_build(repo_url,opts)

application = tornado.web.Application([
    (r"/", MainHandler),
])


# start the script on httpd
if __name__ == "__main__":
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
