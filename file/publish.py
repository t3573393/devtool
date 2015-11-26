#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pexpect
import os
import logging
import sys

conf = {
    "user": "root",
    "host": "your host name",
    "port": 22,
    "password": "your passport",
    "dest": "remote file directory",
    "exclude": [".idea", ".git", "*.log", "*_local.json", "test*", "*.pyc", "*.json", ],  # the exclue path
    "git-commit": "the git commit id"
}

if __name__ == "__main__":
    # set working path
    logging.basicConfig(level=logging.DEBUG)

    project = os.path.split(os.path.realpath(__file__))[0]
    if sys.argv:
        project = sys.argv[1]
    logging.debug('change path to %s' % project)
    os.chdir(project)

    file_list = list()
    logging.debug('retrieve from git')
    result = os.popen("git ls-tree --name-only -r %s" % conf['git-commit']).readlines()
    logging.debug('execute: %s' % "git ls-tree --name-only -r %s" % conf['git-commit'])
    for a_line in result:
        new_line = a_line.replace('\n', '')
        file_list.append(new_line)
        logging.debug('find %s' % new_line)

    # file rsync
    excl = " ".join(["--exclude " + item for item in conf["exclude"]])
    if file_list:
        logging.debug('use files from git')
        for a_file in file_list:
            cmd = "rsync -e 'ssh -p %d' -aP %s %s %s@%s:%s" % (conf['port'], excl, a_file, conf["user"], conf["host"], conf["dest"])
            # use pexpect
            logging.debug('execute: %s' % cmd)
            child = pexpect.spawn(cmd)
            child.expect('password:')
            child.sendline(conf['password'])
            child.interact()
    else:
        # use all file
        cmd = "rsync -e 'ssh -p %d' -aP %s . %s@%s:%s" % (conf['port'], excl, conf["user"], conf["host"], conf["dest"])
        # use pexpect
        logging.debug('execute: %s' % cmd)
        child = pexpect.spawn(cmd)
        child.expect('password:')
        child.sendline(conf['password'])
        child.interact()

