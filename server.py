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


# configuration file directives
# log file
# source directory
# sqlite database location
CONFIG_FILES = [
    '/etc/gitserver.cfg',
    os.path.expanduser('~/.gitserver.cfg'),
]

CONFIG_OPTS = {
    'log_file' : '',
    'repo_dir' : '',
    'database' : '',
}


# parse the configuration file
config = ConfigParser.ConfigParser()
config_files = config.read(CONFIG_FILES)
if not config_files:
    fatal_error('configuration file not found')

if not config.has_section('default'):
    fatal_error('configuration error, [default] section not found')

for opt in CONFIG_OPTS:
    if not config.has_option('default', opt):
        fatal_error('configuration error, [default] section missing option "%s"' % opt)

    CONFIG_OPTS[opt] = config.get('default', opt)

    if not CONFIG_OPTS[opt]:
        fatal_error('configuration error, option "%s" is empty' % opt)


# setup logging
logging.basicConfig(filename=CONFIG_OPTS['log_file'], format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")


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

Log.info('command: %s' % command)


# check on the repository
r = Repository(name = reponame, directory = CONFIG_OPTS['repo_dir'])

if not r.name:
    msg = 'repository name "%s" is invalid' % re.sub('\'', '', reponame)
    Log.critical(msg)
    fatal_error(msg)

if not r.exists():
    msg = 'repository "%s" does not exist' % r.name
    Log.critical(msg)
    fatal_error(msg)

Log.info('repository: %s' % r.name)


# setup the database connection
d = Database(CONFIG_OPTS['database'])


# check the repo permissions and execute the requested command if allowed
perm_requested = COMMANDS[command]
Log.info('permission requested: %s (%d)' % (Permission.name[perm_requested], perm_requested))

perm_allowed = d.permission(r.name, username)
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

