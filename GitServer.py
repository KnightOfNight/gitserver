

import logging
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time


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
            logging.critical('repository "%s" already exists' % (self.name))
            return(False)

        if not os.path.isdir(self.path):
            os.mkdir(self.path)

        stdout = tempfile.mkstemp(dir = "/tmp")
        stdout_fd = stdout[0]
        stdout_file = stdout[1]

        cmd = 'git init --bare %s' % self.path

        cmd_ret = subprocess.call(cmd, stdout = stdout_fd, stderr = subprocess.STDOUT, shell = True)

        os.close(stdout_fd)

        if cmd_ret == 0:
            ret = True

        else:
            logging.critical('unable to initialize git repository')

            with open(stdout_file) as f:
                print f.readline()

            ret = False
            
        os.unlink(stdout_file)
            
        return(ret)

    def delete(self):
        if not self.exists():
            logging.critical('repository "%s" does not exist' % (self.name))
            return(False)

        shutil.rmtree(self.path)


# database schema
# table users
#   name, unique
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
        self.conn.execute('CREATE TABLE IF NOT EXISTS users (name text unique, key text unique, created_at int, updated_at int)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS permissions (repository_name text, user_name text, permission int, created_at int, updated_at int)')

    def get_user(self, username = None):
        c = self.conn

        if username == None:
            cur = c.execute('SELECT name,key FROM users')
        else:
            cur = c.execute('SELECT name,key FROM users WHERE name=?', (username,))

        return(cur.fetchall())

    def create_user(self, username, userkey):
        c = self.conn

        if self.get_user(username):
            logging.critical('user "%s" already exists')
            return(False)

        t = int(time.time())

        try:
            with c:
                c.execute('INSERT INTO users VALUES(?, ?, ?, ?)', (username, userkey, t, t))
                return(True)

        except sqlite3.IntegrityError:
            logging.critical('user or key already exists')
            return(False)

    def delete_user(self, username):
        c = self.conn

        if not self.get_user(username):
            logging.critical('user "%s" does not exist' % (username))
            return(False)

        with c:
            c.execute('DELETE FROM users WHERE name=?', (username,))
            c.execute('DELETE FROM permissions WHERE user_name=?', (username,))

        logging.debug(str(c.total_changes) + ' rows deleted')

        return(True)

    def get_permission(self, reponame, username):
        c = self.conn

        cur = c.execute('SELECT permission FROM permissions WHERE user_name=? AND repository_name=?', (username, reponame))

        permission = cur.fetchone()

        if permission == None:
            permission = 0
        else:
            permission = int(permission[0])

        return(permission)

    def create_permission(self, reponame, username, permission):
        c = self.conn

        if not self.get_user(username):
            logging.critical('user "%s" does not exist')
            return(False)

        t = int(time.time())

        if self.get_permission(reponame, username):
            # update
            with c:
                c.execute('UPDATE permissions SET permission=?,updated_at=? WHERE repository_name=? AND user_name=?', (permission, t, reponame, username))

        else:
            # insert
            with c:
                c.execute('INSERT INTO permissions VALUES(?, ?, ?, ?, ?)', (reponame, username, permission, t, t))

        return(True)

    def delete_permission(self, reponame, username):
        c = self.conn

        if not c.get_permission(reponame, username):
            logging.critical('user "%s" does not have any permissions for repository "%s"' % (username, reponame))
            return(False)

        with c:
            c.execute('DELETE FROM permissions WHERE repository_name=? AND user_name=?', (reponame, username))

        logging.debug(str(c.total_changes) + ' rows deleted')

        return(True)

    def delete_all_permissions(self, reponame):
        c = self.conn

        with c:
            c.execute('DELETE FROM permissions WHERE repository_name=?', (reponame,))

        logging.debug(str(c.total_changes) + ' rows deleted')

        return(True)

