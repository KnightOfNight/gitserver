import os

class Repository:
    def __init__(self, name, directory = ""):
        self.name = name
        self.directory = directory

    def exists(self):
        path = self.directory + "/" + self.name

        return os.path.exists(path)
