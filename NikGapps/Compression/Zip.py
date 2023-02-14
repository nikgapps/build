from zipfile import ZipFile, ZIP_DEFLATED

from NikGapps.Helper.FileOp import FileOp


class Zip:
    def __init__(self, name):
        FileOp.create_file_dir(name)
        self.zipObj = ZipFile(name, 'w', compression=ZIP_DEFLATED)

    def add_file(self, filename, zippath):
        self.zipObj.write(filename, zippath)

    def add_string(self, text, filename):
        self.zipObj.writestr(filename, text)

    def close(self):
        self.zipObj.close()
