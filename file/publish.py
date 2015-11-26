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
    project = os.path.split(os.path.realpath(__file__))[0]
    os.chdir(project)

    file_list = list()
    logging.debug('retrieve from git')
    result = os.popen("git diff-tree --no-commit-id --name-only -r %s" % conf['git-commit']).readlines()
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
        cmd = "rsync -e 'ssh -p %d' -aP %s %s %s@%s:%s" % (conf['port'], excl, a_file, conf["user"], conf["host"], conf["dest"])
        # use pexpect
        logging.debug('execute: %s' % cmd)
        child = pexpect.spawn(cmd)
        child.expect('password:')
        child.sendline(conf['password'])
        child.interact()

