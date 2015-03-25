
import os
import sqlite3
import sys

def fatal_error(msg):
    sys.stderr.write(msg)
    sys.exit(-1)

class Permissions:
    read = 1
    write = 2

class Repository:
    def __init__(self, name, directory = ""):
        self.name = name
        self.directory = directory

    def exists(self):
        path = self.directory + "/" + self.name
        return os.path.exists(path)

class Database:
    def __init__(self, file):
        self.file = file
        self.conn = sqlite3.connect(file)
        self.conn.execute('CREATE TABLE IF NOT EXISTS users (name text, key text)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS permissions (repository_name text, user_name text, permission int)')

    def permission(self, reponame, username):
        c = self.conn
        cur = c.execute('SELECT p.permission FROM permissions AS p WHERE p.user_name='?' AND p.repository_name='?'', (username, reponame))
        permission = cur.fetchone()
        return(permission)

