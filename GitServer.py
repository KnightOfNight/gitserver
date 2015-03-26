

import os
import re
import sqlite3
import sys


def fatal_error(msg):
    tag = "gitserver fatal error: "
    sys.stderr.write(tag + msg + "\n")
    sys.exit(-1)


class Permission:
    read = 1
    write = 2
    name = [ "none", "read", "write" ]


class Repository:
    def __init__(self, name, directory = ""):
        self.name = re.sub('[^a-zA-Z0-9]', '', name)
        self.directory = directory
        self.path = self.directory + "/" + self.name

    def exists(self):
        if not self.name:
            return False

        elif not os.path.isdir(self.path) or \
                not os.path.isfile(self.path + "/config") or \
                not os.path.isfile(self.path + "/description") or \
                not os.path.isfile(self.path + "/HEAD") or \
                not os.path.isdir(self.path + "/branches") or \
                not os.path.isdir(self.path + "/hooks") or \
                not os.path.isdir(self.path + "/info") or \
                not os.path.isdir(self.path + "/objects") or \
                not os.path.isdir(self.path + "/refs"):
            return False

        else:
            return True


# database schema
# table users
#   name
#   key
# table permissions
#   repository_name
#   user_name
#   permission
class Database:
    def __init__(self, file):
        self.file = file
        self.conn = sqlite3.connect(file)
        self.conn.execute('CREATE TABLE IF NOT EXISTS users (name text, key text)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS permissions (repository_name text, user_name text, permission int)')

    def permission(self, reponame, username):
        c = self.conn

        cur = c.execute('SELECT p.permission FROM permissions AS p WHERE p.user_name=? AND p.repository_name=?', (username, reponame))

        permission = cur.fetchone()

        if permission == None:
            permission = 0
        else:
            permission = int(permission[0])

        return(permission)

