#!/usr/bin/python


import argparse
import ConfigParser
import logging
import re
import os
import sqlite3
import string
import sys

from GitServer import Repository


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
    sys.stderr.write('Configuration error: file not found. Must be one of: %s\n' % ', '.join(s for s in CONFIG_FILES))
    sys.exit(-1)

if not config.has_section('default'):
    sys.stderr.write('Configuration error: [default] section not found.\n')
    sys.exit(-1)

for opt in CONFIG_OPTS:
    if not config.has_option('default', opt):
        sys.stderr.write('Configuration error: [default] section missing "%s".\n' % opt)
        sys.exit(-1)

    CONFIG_OPTS[opt] = config.get('default', opt)

    if not CONFIG_OPTS[opt]:
        sys.stderr.write('Configuration error: option "%s" is empty.\n' % opt)
        sys.exit(-1)


# setup logging
logging.basicConfig(filename=CONFIG_OPTS['log_file'], format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)


# parse command line arguments
parser = argparse.ArgumentParser(description='Process a git command as called via an SSH connection.')
parser.add_argument('-u', '--username', required=True, help='Name of the gitserver user account.')
args = parser.parse_args()

username = args.username


logging.info('User "%s" connected to git server.' % username)


# parse the specified command
original_cmd = os.environ.get('SSH_ORIGINAL_COMMAND')

if original_cmd == None:
    msg = 'No command provided in SSH_ORIGINAL_COMMAND, user attempted to access shell.'
    logging.critical(msg)
    msg = 'You have successfully authenticated, but this server does not provide shell access.\n'
    sys.stderr.write(msg)
    sys.exit(-1)

parsed_cmd = string.split(original_cmd, ' ')

if len(parsed_cmd) != 2:
    msg = 'Received invalid command "%s".' % original_cmd
    logging.critical(msg)
    msg = 'You must pass a single command with exactly one argument.\n'
    sys.stderr.write(msg)
    sys.exit(-1)

command = parsed_cmd[0]
repo_name = re.sub('\'', '', parsed_cmd[1])

if not command in COMMANDS:
    msg = 'Received invalid command "%s".' % original_cmd
    logging.critical(msg)
    msg = '"%s" is not a valid command. Must be one of: %s\n' % (command, ', '.join(s for s in COMMANDS.keys()))
    sys.stderr.write(msg)
    sys.exit(-1)


r = Repository(name = repo_name, directory = CONFIG_OPTS['repo_dir'])
print r.exists()


sys.exit(0)

