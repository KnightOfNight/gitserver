#!/usr/bin/python


import argparse
import ConfigParser
import logging
import re
import os
import sqlite3
import string
import sys

from GitServer import fatal_error
from GitServer import Permissions
from GitServer import Repository
from GitServer import Database


# allowed Git commands
# git-upload-pack
# git-upload-archive
# git-receive-pack
COMMANDS = {
    'git-upload-pack' : Permissions.read,
    'git-upload-archive' : Permissions.read,
    'git-receive-pack' : Permissions.write,
}


# schema
# table users
#   id
#   user name
#   user SSH key
# table repositories
#   id
#   name
# table permissions
#   id
#   repository name
#   user name
#   permission


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


# command line arguments
# SSH key, --key


# parse the configuration file
config = ConfigParser.ConfigParser()
config_files = config.read(CONFIG_FILES)
if not config_files:
    fatal_error('Configuration file not found. Must be one of: %s\n' % ', '.join(s for s in CONFIG_FILES))

if not config.has_section('default'):
    fatal_error('Configuration error: [default] section not found.\n')

for opt in CONFIG_OPTS:
    if not config.has_option('default', opt):
        fatal_error('Configuration error: [default] section missing "%s".\n' % opt)

    CONFIG_OPTS[opt] = config.get('default', opt)

    if not CONFIG_OPTS[opt]:
        fatal_error('Configuration error: option "%s" is empty.\n' % opt)


# setup logging
logging.basicConfig(filename=CONFIG_OPTS['log_file'], format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)


# parse command line arguments
parser = argparse.ArgumentParser(description='Process a git command as called via an SSH connection.')
parser.add_argument('-u', '--username', required=True, help='Name of the gitserver user account.')
args = parser.parse_args()

username = args.username

logging.info('Username = "%s".' % username)


# parse the specified command
original_cmd = os.environ.get('SSH_ORIGINAL_COMMAND')

if original_cmd == None:
    msg = 'Successfully authenticated, but this server does not provide shell access.'
    logging.critical(msg)
    fatal_error(msg + '\n')

parsed_cmd = string.split(original_cmd, ' ')

if len(parsed_cmd) != 2:
    msg = 'Received invalid command "%s".' % original_cmd
    logging.critical(msg)
    fatal_error(msg + '\n')

command = parsed_cmd[0]
reponame = re.sub('\'', '', parsed_cmd[1])

if command in COMMANDS:
    logging.info('Command = "%s".' % command)

else:
    msg = 'Received invalid command "%s". Must be one of: %s' % (command, ', '.join(s for s in COMMANDS.keys()))
    logging.critical(msg)
    fatal_error(msg + '\n')


# check on the repository
r = Repository(name = reponame, directory = CONFIG_OPTS['repo_dir'])

if r.exists():
    logging.info('Repository = "%s".' % reponame)

else:
    msg = 'Repository "%s" does not exist.' % reponame
    logging.critical(msg)
    fatal_error(msg + '\n')


# setup the database connection
d = Database(CONFIG_OPTS['database'])


# check the repo permissions and execute the requested command if allowed
perm_needed = COMMANDS[command]


if perm_needed == Permissions.read:
    logging.info('Read access requested.')

elif COMMANDS[command] == Permissions.write:
    logging.info('Write access requested.')


if d.permission(reponame, username) == perm_needed:
    logging.info('User "%s" has permission to access repository, executing requested command.' % username)
    cmd = "%s %s/%s" % (command, CONFIG_OPTS['repo_dir'], reponame)
    logging.info('Command = "%s".' % cmd)
    os.system(cmd)

else:
    logging.info('User "%s" does not have the required permission.' % username)
    fatal_error('You do not have permission to access "%s".\n' % repo_name)


sys.exit(0)

