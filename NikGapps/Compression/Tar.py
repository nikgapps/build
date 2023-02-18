import tarfile
from io import BytesIO


class Tar:

    def __init__(self, file_name, folder_to_compress=None):
        if folder_to_compress is None:
            self.folder = folder_to_compress
        self.tarfile = str(file_name) if str(file_name).endswith("tar.xz") else str(file_name) + ".tar.xz"
        self.tar = tarfile.open(self.tarfile, "w:xz")

    def add_file(self, file_to_add, zippath):
        self.tar.add(file_to_add, arcname=zippath)

    def add_string(self, text, file_name):
        data = text.encode('utf-8')
        info = tarfile.TarInfo(name=file_name)
        info.size = len(data)
        self.tar.addfile(tarinfo=info, fileobj=BytesIO(data))

    def close(self):
        self.tar.close()
