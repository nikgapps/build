from zipfile import ZipFile
from zipfile import ZIP_DEFLATED
from .FileOp import FileOp


class ZipOp:
    def __init__(self, name):
        FileOp.create_file_dir(name)
        self.zipObj = ZipFile(name, 'w', compression=ZIP_DEFLATED)

    def writefiletozip(self, filename, zippath):
        self.zipObj.write(filename, zippath)

    def writestringtozip(self, text, filename):
        self.zipObj.writestr(filename, text)

    def close(self):
        self.zipObj.close()
