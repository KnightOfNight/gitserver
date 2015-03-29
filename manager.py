#!/bin/env python


import argparse
import logging
import os
import sys

from GitServer import Config
from GitServer import Permission
from GitServer import Database
from GitServer import Repository


def generate_authorized_keys(config_opts):
    dir = os.path.expanduser('~/.ssh')
    file = os.path.expanduser(dir + '/authorized_keys')

    if not os.path.isdir(dir):
        os.mkdir(dir, 0700)

    d = Database(config_opts['database'])

    users = d.get_user()

    with open(file, "w") as f:
        for user in users:
            name = user[0]
            key = user[1]
            f.write('command="%s --username %s",no-port-forwarding,no-X11-forwarding,no-pty %s\n' % (config_opts['server_script'], name, key))

    os.chmod(file, 0600)


def confirm_deletion(description, value):
    yesno = raw_input('Are you sure you want to delete the %s "%s" [yes/NO]? ' % (description, value))
    print

    if yesno != 'yes':
        logging.warn('%s will not be deleted' % (description))
        return(False)

    yesno = raw_input('This cannot be undone.  Type "yes" again to confirm: ')
    print

    if yesno != 'yes':
        logging.warn('%s will not be deleted' % (description))
        return(False)

    return(True)


# load the config
config_opts = Config.get()


# setup logging
logging.basicConfig(format = '%(levelname)s: %(message)s', level = logging.DEBUG)


# parse command line arguments
parser = argparse.ArgumentParser(description = 'Manage repositories, uers, and permissions.')

mode = parser.add_subparsers(title = 'mode')

# repo mode arguments
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

# user mode arguments
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

# perm mode arguments
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

# do the actual parse args
args = parser.parse_args()


# do something
mode = args.mode
cmd = args.cmd

d = Database(config_opts['database'])

if mode == 'repo':

    if cmd == 'create':
        reponame = args.name

        r = Repository(reponame, config_opts['repo_dir'])

        logging.info('creating repository "%s"' % (reponame))

        if not r.create():
            sys.exit(-1)

    elif cmd == 'delete':
        reponame = args.name

        r = Repository(reponame, config_opts['repo_dir'])

        if not confirm_deletion('repository', reponame):
            sys.exit(0)

        logging.info('deleting repository "%s"' % (reponame))

        if not r.delete():
            sys.exit(-1)

        logging.info('deleting all permissions on repository "%s"' % (reponame))

        d.delete_all_permissions(reponame)    

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

        logging.info('creating user "%s"' % (username))

        if not d.create_user(username, userkey):
            sys.exit(-1)

    elif cmd == 'delete':
        username = args.name

        if not confirm_deletion('user', username):
            sys.exit(0)

        logging.info('deleting user "%s"' % (username))

        if not d.delete_user(username):
            sys.exit(-1)

        generate_authorized_keys(config_opts)

    elif cmd == 'list':
        users = d.get_user()

        print "Users"
        print "---------------------"
        for user in users:
            print "%s" % (user[0])

elif mode == 'perm':
    d = Database(config_opts['database'])

    if cmd == "create":
        username = args.user
        permission = args.perm
        reponame = args.repo

        logging.info('creating "%s" permission for user "%s" on repository "%s"' % (permission, username, reponame))

        r = Repository(reponame, config_opts['repo_dir'])

        if not r.exists():
            logging.critical('repository "%s" does not exist' % (reponame))
            sys.exit(-1)

        d.create_permission(reponame, username, Permission.name.index(permission))

        generate_authorized_keys(config_opts)

    elif cmd == "delete":
        username = args.user
        reponame = args.repo

        if not confirm_deletion('permission', "%s %s" % (username, reponame)):
            sys.exit(0)

        logging.info('deleting permissions for user "%s" on repository "%s"' % (username, reponame))

        d.delete_permission(reponame, username)

        generate_authorized_keys(config_opts)

sys.exit(0)

