import os
import sqlite3

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

