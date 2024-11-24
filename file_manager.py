from utils import Singleton


class FileManager(metaclass=Singleton):
    base_path = 'data/'

    def __init__(self):
        self.files = []

    def add_file(self, file_name):
        self.files.append(file_name)

    def get_files(self):
        return self.files

