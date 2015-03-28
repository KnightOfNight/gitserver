

import os
import re
import sqlite3
import subprocess
import sys
import tempfile


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

        elif not os.path.isdir(self.path):
            return False

        elif os.path.isfile(self.path + "/config") and \
                os.path.isfile(self.path + "/description") and \
                os.path.isfile(self.path + "/HEAD") and \
                os.path.isdir(self.path + "/branches") and \
                os.path.isdir(self.path + "/hooks") and \
                os.path.isdir(self.path + "/info") and \
                os.path.isdir(self.path + "/objects") and \
                os.path.isdir(self.path + "/refs"):
            return True

        else:
            return False

    def create(self):
        if self.exists():
            logging.critical('repository already exists')
            return(False)

        if not os.path.isdir(self.path):
            os.mkdir(self.path)

        stdout = tempfile.mkstemp(dir = "/tmp")
        stdout_fd = stdout[0]
        stdout_file = stdout[1]

        cmd = "git init --bare %s" % self.path

        cmd_ret = subprocess.call(cmd, stdout = stdout_fd, stderr=subprocess.STDOUT)

        os.close(stdout_fd)

        if cmd_ret == 0:
            logging.info('repository created successfully')
            ret = True

        else:
            logging.critical('unable to initialize git repository')

            with open(stdout_file) as f:
                print f.readline()

            ret = False
            
        os.unlink(stdout_file)
            
        return(ret)

    def delete(self):
        if not self.exsits():
            logging.critical('repository does not exist')
            return(False)

        shutil.rmtree(self.path)


# database schema
# table users
#   name
#   key
#   created_at
#   updated_at
# table permissions
#   repository_name
#   user_name
#   permission
#   created_at
#   updated_at
class Database:
    def __init__(self, file):
        self.file = file
        self.conn = sqlite3.connect(file)
        self.conn.execute('CREATE TABLE IF NOT EXISTS users (name text, key text)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS permissions (repository_name text, user_name text, permission int)')

    def get_permission(self, reponame, username):
        c = self.conn

        cur = c.execute('SELECT p.permission FROM permissions AS p WHERE p.user_name=? AND p.repository_name=?', (username, reponame))

        permission = cur.fetchone()

        if permission == None:
            permission = 0
        else:
            permission = int(permission[0])

        return(permission)

