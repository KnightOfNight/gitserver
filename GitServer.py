import os
import sqlite3
import sys

def fatal_error(msg):
    sys.stderr.write(msg)
    sys.exit(-1)

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

    def repo_readable(self, repo_name, user_name):
# query = "select p.permission from permissions as p where p.user_name='USER_NAME' and p.repository_name='REPO_NAME';"

    def repo_writable(self, repo_name, user_name):
# query = "select p.permission from permissions as p where p.user_name='USER_NAME' and p.repository_name='REPO_NAME';"

