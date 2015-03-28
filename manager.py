#!/bin/env python


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


mode = args.mode
cmd = args.cmd


if mode == 'repo':
    reponame = args.name

    r = Repository(reponame, config_opts['repo_dir'])

    if cmd == 'create':
        logging.info('creating repository %s', reponame)

        if not r.create():
            sys.exit(-1)

    elif cmd == 'delete':
        yesno = raw_input('Are you sure you want to delete the repository "%s"?  This cannot be undone. [yes/NO] ' % reponame)

        if yesno != 'yes':
            print 'Repository will not be deleted'
            sys.exit(0)

        yesno = raw_input('Verify the name of the repository: ')

        if yesno != reponame:
            print 'Repository will not be deleted'
            sys.exit(0)

        logging.info('deleting repository %s', reponame)

        if not r.delete():
            sys.exit(-1)

elif mode == 'user':
    username = args.name

    d = Database(config_opts['database'])

    if cmd == 'create':
        userkey = raw_input('Copy and paste the SSH key user "%s": ' % username)

        k = userkey.split(' ')

        if len(k) < 2 or len(k) > 3:
            logging.critical('SSH key is invalid, expecting key in the format "<tag> <key> [<comment>]"')

        if len(k) == 3:
            k.pop()

        userkey = ' '.join(k)

        logging.info('creating user %s', username)

        d.create_user(username, userkey)

    elif cmd == 'delete':
        logging.info('deleting user %s', username)

elif mode == 'perm':
    print 'perm mode'


sys.exit(0)

