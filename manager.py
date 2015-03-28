#!/usr/bin/python


import argparse
import logging
import sys

import Config
from GitServer import Permission
from GitServer import Database
from GitServer import Repository


# repo create <repo>

# repo delete <repo>

# user create <user>

# user update <user>

# user delete <user>

# permission add read|write <repo> <user>

# permission remove read|write <repo> <user>


logging.basicConfig(format = '%(levelname)s: %(message)s', level = logging.DEBUG)


config_opts = Config.get()


parser = argparse.ArgumentParser(description = 'Manage repositories, uers, and permissions.')

mode = parser.add_subparsers(title = 'mode')

# repo mode argument parsing
repo = mode.add_parser('repo')
repo.set_defaults(mode='repo')

sp = repo.add_subparsers(title = 'command')

cmd = 'create'
p = sp.add_parser(cmd)
p.set_defaults(cmd = cmd)
p.add_argument('name')

cmd = 'delete'
p = sp.add_parser(cmd)
p.set_defaults(cmd = cmd)
p.add_argument('name')

cmd = 'list'
p = sp.add_parser(cmd)
p.set_defaults(cmd = cmd)

# user mode argument parsing
user = mode.add_parser('user')
user.set_defaults(mode='user')

sp = user.add_subparsers(title = 'command')

cmd = 'create'
p = sp.add_parser(cmd)
p.set_defaults(cmd = cmd)
p.add_argument('name')

cmd = 'delete'
p = sp.add_parser(cmd)
p.set_defaults(cmd = cmd)
p.add_argument('name')

cmd = 'list'
p = sp.add_parser(cmd)
p.set_defaults(cmd = cmd)

# perm mode argument parsing
perm = mode.add_parser('perm')
perm.set_defaults(mode='perm')

sp = perm.add_subparsers(title = 'command')

cmd = 'create'
p = sp.add_parser(cmd)
p.set_defaults(cmd = cmd)
p.add_argument('user')
p.add_argument('perm', choices = [ Permission.name[Permission.read], Permission.name[Permission.write] ])
p.add_argument('repo')

cmd = 'delete'
p = sp.add_parser(cmd)
p.set_defaults(cmd = cmd)
p.add_argument('user')
p.add_argument('perm', choices = [ Permission.name[Permission.read], Permission.name[Permission.write] ])
p.add_argument('repo')

cmd = 'list'
p = sp.add_parser(cmd)
p.set_defaults(cmd = cmd)

# parse args
args = parser.parse_args()

print args

print config_opts


if args.mode == 'repo':
    r = Repository(args.repo, config_opts['repo_dir'])

    if args.cmd == 'create':
        logging.info('creating repository %s', args.name)

        if not r.create():
            sys.exit(-1)

    elif args.cmd == 'delete':
        logging.info('deleting repository %s', args.name)

        if not r.delete():
            sys.exit(-1)

elif mode == 'user':
    print 'user mode'

elif mode == 'perm':
    print 'perm mode'


sys.exit(0)

