#!/usr/bin/python


import argparse
import ConfigParser
import logging
import re
import os
import sqlite3
import string
import sys


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
    "git-upload-pack": PERM_READ,
    "git-upload-archive": PERM_READ,
    "git-receive-pack": PERM_WRITE,
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


# command line arguments
# SSH key, --key


# methods
# repository.exists(name)
# repository.writable(user)
# repository.readable(user)


config = ConfigParser.ConfigParser()
config_files = config.read(CONFIG_FILES)
if not config_files:
    sys.stderr.write("Configuration file not found. Must be one of: %s\n" % ", ".join(s for s in CONFIG_FILES))
    sys.exit(-1)

if not config.has_section('default'):
    sys.stderr.write("[default] section not found in any configuration file.\n")
    sys.exit(-1)

log_file = config.get('default', 'log'):



original_cmd = os.environ.get('SSH_ORIGINAL_COMMAND')

if original_cmd == None:
    sys.stderr.write("You have successfully authenticated, but this server does not provide shell access.\n")
    sys.exit(-1)


parsed_cmd = string.split(original_cmd, ' ')

if len(parsed_cmd) != 2:
    sys.stderr.write("You must pass a single command with exactly one argument.\n")
    sys.exit(-1)


command = parsed_cmd[0]
repository = re.sub('\'', '', parsed_cmd[1])

if not command in COMMANDS:
    sys.stderr.write("'%s' is not a valid command. Must be one of: %s\n" % (command, ", ".join(s for s in COMMANDS.keys())))
    sys.exit(-1)

