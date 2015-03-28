#!/usr/bin/python


import argparse
import ConfigParser
import logging
import os
import re
import sqlite3
import string
import sys
import time

import Config
from Log import Log
from GitServer import fatal_error
from GitServer import Permission
from GitServer import Repository
from GitServer import Database


# allowed Git commands
# git-upload-pack
# git-upload-archive
# git-receive-pack
COMMANDS = {
    'git-upload-pack' : Permission.read,
    'git-upload-archive' : Permission.read,
    'git-receive-pack' : Permission.write,
}


# load the config
config_opts = Config.get()


# setup logging
logging.basicConfig(filename=config_opts['log_file'], format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

Log.info('session start')


# parse command line arguments
parser = argparse.ArgumentParser(description='Process a git command as accessed via an SSH connection.')
parser.add_argument('-u', '--username', required=True, help='Name of the gitserver user account.')
args = parser.parse_args()

username = args.username

Log.info('username: %s' % username)


# parse the specified command
original_command = os.environ.get('SSH_ORIGINAL_COMMAND')

if original_command == None:
    msg = 'SSH_ORIGINAL_COMMAND is empty'
    Log.critical(msg)

    msg = 'no Git command specified, server does not provide shell access'
    fatal_error(msg)

Log.info('SSH_ORIGINAL_COMMAND: %s' % original_command)

parsed_command = string.split(original_command, ' ')

if len(parsed_command) != 2:
    msg = 'command "%s" is invalid' % original_command
    Log.critical(msg)
    fatal_error(msg)

command = parsed_command[0]
reponame = parsed_command[1]

if not command in COMMANDS:
    msg = 'command "%s" is invalid' % original_command
    Log.critical(msg)
    fatal_error(msg)

Log.info('parsed command: %s' % command)


# check on the repository
r = Repository(name = reponame, directory = config_opts['repo_dir'])

if not r.name:
    msg = 'repository name "%s" is invalid' % re.sub('\'', '', reponame)
    Log.critical(msg)
    fatal_error(msg)

if not r.exists():
    msg = 'repository "%s" does not exist' % r.name
    Log.critical(msg)
    fatal_error(msg)

Log.info('parsed (and sanitized) repository: %s' % r.name)


# setup the database connection
d = Database(config_opts['database'])


# check the repo permissions and execute the requested command if allowed
perm_requested = COMMANDS[command]
Log.info('permission requested: %s (%d)' % (Permission.name[perm_requested], perm_requested))

perm_allowed = d.get_permission(r.name, username)
Log.info('permission allowed: %s (%d)' % (Permission.name[perm_allowed], perm_allowed))

if perm_requested <= perm_allowed:
    cmd = "%s %s" % (command, r.path)
    Log.info('access granted, executing command: %s' % cmd)
    os.system(cmd)

else:
    msg = 'access denied'
    Log.critical(msg)

    msg += ', you are not allowed %s access to the repository' % Permission.name[perm_requested]
    fatal_error(msg)


sys.exit(0)

