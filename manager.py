#!/usr/bin/python


import argparse

from GitServer import Permission


# load config, need repo dir

# repo create <repo>

# repo delete <repo>

# user create <user>

# user update <user>

# user delete <user>

# permission add read|write <repo> <user>

# permission remove read|write <repo> <user>


parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help = 'commands')

parser_repo = subparsers.add_parser('repo', help = 'repository management')
parser_repo.add_argument('command', choices = [ 'create', 'delete'], help = 'action to take')
parser_repo.add_argument('name', help = 'name of the repository')

parser_user = subparsers.add_parser('user', help = 'user management')
parser_user.add_argument('command', choices = [ 'create', 'update', 'delete'], help = 'action to take')
parser_user.add_argument('name', help = 'name of the user')

parser_perm = subparsers.add_parser('perm', help = 'permission management')
parser_perm.add_argument('command', choices = [ 'add', 'remove'], help = 'action to take')
parser_perm.add_argument('user', help = 'name of the user')
parser_perm.add_argument('permission', choices = [ Permission.name[Permission.read], Permission.name[Permission.write] ], help = 'permission to grant')
parser_perm.add_argument('repo', help = 'name of the repository')

args = parser.parse_args()

