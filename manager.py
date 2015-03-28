#!/bin/env python


import argparse
import logging
import os
import sys

import Config
from GitServer import Permission
from GitServer import Database
from GitServer import Repository


def generate_authorized_keys(config_opts):
    dir = os.path.expanduser('~/.ssh')
    file = os.path.expanduser(dir + '/authorized_keys')

    if not os.path.isdir(dir):
        os.mkdir(dir, 0700)

    d = Database(config_opts['database'])

    users = d.get_users()

    with open(file, "w") as f:
        for user in users:
            name = user[0]
            key = user[1]
            f.write('command="%s --username %s",no-port-forwarding,no-X11-forwarding,no-pty %s\n' % (config_opts['server_script'], name, key))

    os.chmod(file, 0600)


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
p.add_argument('repo')

cmd = 'list'
p = sp.add_parser(cmd)
p.set_defaults(cmd = cmd)

# parse args
args = parser.parse_args()


# do something
mode = args.mode
cmd = args.cmd

if mode == 'repo':

    if cmd == 'create':
        reponame = args.name

        r = Repository(reponame, config_opts['repo_dir'])

        logging.info('creating repository %s', reponame)

        if not r.create():
            sys.exit(-1)

    elif cmd == 'delete':
        reponame = args.name

        r = Repository(reponame, config_opts['repo_dir'])

        yesno = raw_input('Are you sure you want to delete the repository "%s"?  This cannot be undone. [yes/NO] ' % reponame)
        print

        if yesno != 'yes':
            logging.warn('repository will not be deleted')
            sys.exit(0)

        yesno = raw_input('Verify the name of the repository: ')
        print

        if yesno != reponame:
            logging.warn('repository will not be deleted')
            sys.exit(0)

        logging.info('deleting repository %s', reponame)

        if not r.delete():
            sys.exit(-1)

elif mode == 'user':

    d = Database(config_opts['database'])

    if cmd == 'create':
        username = args.name

        userkey = raw_input('Copy and paste the SSH key user "%s": ' % username)
        print

        k = userkey.split(' ')

        if len(k) < 2 or len(k) > 3:
            logging.critical('SSH key is invalid, expecting key in the format "<tag> <key> [<comment>]"')
            sys.exit(-1)

        if len(k) == 3:
            k.pop()

        userkey = ' '.join(k)

        logging.info('creating user %s', username)

        if not d.create_user(username, userkey):
            sys.exit(-1)

    elif cmd == 'delete':
        username = args.name

        yesno = raw_input('Are you sure you want to delete the user "%s"?  This cannot be undone. [yes/NO] ' % username)
        print

        if yesno != 'yes':
            logging.warn('user will not be deleted')
            sys.exit(0)

        yesno = raw_input('Verify the name of the user: ')
        print

        if yesno != username:
            logging.warn('user will not be deleted')
            sys.exit(0)

        logging.info('deleting user %s', username)

        if not d.delete_user(username):
            sys.exit(-1)

        generate_authorized_keys(config_opts)

elif mode == 'perm':
    print 'perm mode'

    if cmd == "create":
        username = args.user
        permission = args.perm
        reponame = args.repo

        d = Database(config_opts['database'])

        logging.info('creating permission %s %s %s' % (username, permission, reponame))

        d.create_permission(reponame, username, permission)

        generate_authorized_keys(config_opts)

    elif cmd == "delete":
        username = args.user
        reponame = args.repo

        d = Database(config_opts['database'])

        logging.info('deleting permission %s * %s' % (username, reponame))

        d.delete_permission(reponame, username)

        generate_authorized_keys(config_opts)

sys.exit(0)

