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

user_cmd = user.add_subparsers(title = 'command')

user_cmd_create = user_cmd.add_parser('create')
user_cmd_create.set_defaults(cmd = 'create')
user_cmd_create.add_argument('name')

user_cmd_delete = user_cmd.add_parser('delete')
user_cmd_delete.set_defaults(cmd = 'create')
user_cmd_delete.add_argument('name')

# perm mode argument parsing
perm = mode.add_parser('perm')
perm.set_defaults(mode='perm')





#mode_subparser = parser.add_subparsers(help = 'mode')
#
#parser_repo = mode_subparser.add_parser('repo', help = 'repository management')
#parser_repo.set_defaults(mode='repo')
#
#repo_command_subparser = parser_repo.add_subparser(help = 'command')
#
#parser_repo_command = parser.add_subparser(help = 'command')
#
#parser_repo.add_argument('command', choices = [ 'create', 'delete', 'list'], help = 'command')
#parser_repo.add_argument('--name', required = False, help = 'name of the repository')
#
#parser_user = mode_subparser.add_parser('user', help = 'user management')
#parser_user.set_defaults(mode='user')
#parser_user.add_argument('command', choices = [ 'create', 'update', 'delete', 'list'], help = 'command')
#parser_user.add_argument('--name', required = False, help = 'name of the user')
#
#parser_perm = mode_subparser.add_parser('perm', help = 'permission management')
#parser_perm.set_defaults(mode='perm')
#parser_perm.add_argument('command', choices = [ 'add', 'remove'], help = 'action to take')
#parser_perm.add_argument('user', help = 'name of the user')
#parser_perm.add_argument('permission', choices = [ Permission.name[Permission.read], Permission.name[Permission.write] ], help = 'permission to grant')
#parser_perm.add_argument('repo', help = 'name of the repository')

args = parser.parse_args()

mode = args.mode
cmd = args.cmd

print args

