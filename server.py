#!/bin/env python


import argparse
import logging
import os
import re
import sqlite3
import string
import sys
import time

from GitServer import fatal_error
from GitServer import Config
from GitServer import Permission
from GitServer import Repository
from GitServer import Database


# logging helper class
class Log:
    def __init__(self):
        self.session_id = "%.5f" % time.time()

    def format(self, msg):
        return("%s %s" % (self.session_id, msg))

    def info(self, msg):
        logging.info(self.format(msg))

    def warning(self, msg):
        logging.warning(self.format(msg))

    def error(self, msg):
        logging.error(self.format(msg))

    def critical(self, msg):
        logging.critical(self.format(msg))


# allowed Git commands
allowed_git_commands = {
    'git-upload-pack' : Permission.read,
    'git-upload-archive' : Permission.read,
    'git-receive-pack' : Permission.write,
}


# load the config
config_opts = Config.get()


# setup logging
logging.basicConfig(filename=config_opts['log_file'], format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

log = Log()

log.info('session start')


# parse command line arguments
parser = argparse.ArgumentParser(description='Process a git command as accessed via an SSH connection.')
parser.add_argument('-u', '--username', required=True, help='Name of the gitserver user account.')
args = parser.parse_args()

username = args.username

log.info('username: %s' % username)


# parse the original command
original_command = os.environ.get('SSH_ORIGINAL_COMMAND')

if original_command == None:
    msg = 'SSH_ORIGINAL_COMMAND is empty'
    log.critical(msg)

    msg = 'no Git command specified, server does not provide shell access'
    fatal_error(msg)

log.info('SSH_ORIGINAL_COMMAND: %s' % original_command)

parsed_command = string.split(original_command, ' ')

if len(parsed_command) != 2:
    msg = 'command "%s" is invalid' % original_command
    log.critical(msg)
    fatal_error(msg)

command = parsed_command[0]
reponame = parsed_command[1]

if not command in allowed_git_commands:
    msg = 'command "%s" is invalid' % original_command
    log.critical(msg)
    fatal_error(msg)

log.info('parsed command: %s' % command)


# check on the repository
r = Repository(name = reponame, directory = config_opts['repo_dir'])

if not r.name:
    msg = 'repository name "%s" is invalid' % reponame
    log.critical(msg)
    fatal_error(msg)

if not r.exists():
    msg = 'repository "%s" does not exist' % r.name
    log.critical(msg)
    fatal_error(msg)

log.info('parsed (and sanitized) repository: %s' % r.name)


# setup the database connection
d = Database(config_opts['database'])


# check the repo permissions and execute the requested command if allowed
perm_requested = allowed_git_commands[command]
log.info('permission requested: %s (%d)' % (Permission.name[perm_requested], perm_requested))

perm = d.get_permissions(r.name, username)
if perm:
    perm_allowed = int(perm[2])
else:
    perm_allowed = 0
# perm_allowed = d.get_permission(r.name, username)
log.info('permission allowed: %s (%d)' % (Permission.name[perm_allowed], perm_allowed))

if perm_requested <= perm_allowed:
    cmd = "%s %s" % (command, r.path)
    log.info('access granted, executing command: %s' % cmd)
    os.system(cmd)

else:
    msg = 'access denied'
    log.critical(msg)

    msg += ', you are not allowed %s access to the repository' % Permission.name[perm_requested]
    fatal_error(msg)


sys.exit(0)

