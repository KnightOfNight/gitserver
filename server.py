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
from GitServer import Repository
from GitServer import Database


# permissions
# 1 read
# 2 write
PERM_READ = 1
PERM_WRITE = 2


# allowed Git commands
# git-upload-pack
# git-upload-archive
# git-receive-pack
COMMANDS = {
    'git-upload-pack' : PERM_READ,
    'git-upload-archive' : PERM_READ,
    'git-receive-pack' : PERM_WRITE,
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


# methods
# repository.exists(name)
# repository.writable(user)
# repository.readable(user)


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
    msg = 'No command provided in SSH_ORIGINAL_COMMAND, user attempted to access shell.'
    logging.critical(msg)

    msg = 'You have successfully authenticated, but this server does not provide shell access.\n'
    fatal_error(msg)

parsed_cmd = string.split(original_cmd, ' ')

if len(parsed_cmd) != 2:
    msg = 'Received invalid command "%s".' % original_cmd
    logging.critical(msg)

    msg = 'You must pass a single command with exactly one argument.\n'
    fatal_error(msg)

command = parsed_cmd[0]
repo_name = re.sub('\'', '', parsed_cmd[1])

if command in COMMANDS:
    logging.info('Command = "%s".' % command)

else:
    msg = 'Received invalid command "%s". Must be one of: %s\n' % (command, ', '.join(s for s in COMMANDS.keys()))
    logging.critical(msg)
    fatal_error(msg)


# check on the repository
r = Repository(name = repo_name, directory = CONFIG_OPTS['repo_dir'])

if r.exists():
    logging.info('Repository = "%s".' % repo_name)

else:
    msg = 'Repository "%s" does not exist.' % repo_name
    logging.critical(msg)
    fatal_error(msg)


# setup the database connection
d = Database(CONFIG_OPTS['database'])


# check the command and the repo permissions
if COMMANDS[command] == PERM_READ:
    logging.info('Read access requested.')

    if d.repo_readable(repository, user):
        logging.info('Repository is readable to user "%s", executing requested command.' % username)

    else:
        msg = 'Repository is not readable to user "%s".' % username
        logging.critical(msg)
        fatal_error(msg)

elif COMMANDS[command] == PERM_WRITE:
    logging.info('Write access requested.')

    if d.repo_writable(repository, user):
        logging.info('Repository is writable to user "%s", executing requested command.' % username)

    else:
        msg = 'Repository is not writable to user "%s".' % username
        logging.critical(msg)
        fatal_error(msg)


sys.exit(0)

