import tarfile
from io import BytesIO


class Tar:

    def __init__(self, file_name, folder_to_compress=None):
        if folder_to_compress is None:
            self.folder = folder_to_compress
        self.tarfile = str(file_name) if str(file_name).endswith("tar.xz") else str(file_name) + ".tar.xz"
        self.tar = tarfile.open(self.tarfile, "w:xz")

    # def compress(self):
    #     start_time = C.start_of_function()
    #     self.tar.add(self.folder, arcname=self.folder.stem)
    #     print(f"py tar filesize: {round(Path(self.tarfile).stat().st_size / (1024 * 1024), 2)} MB")
    #     C.end_of_function(start_time, "py tar filesize")

    def add_file(self, file_to_add, zippath):
        self.tar.add(file_to_add, arcname=zippath)

    def add_string(self, text, file_name):
        data = text.encode('utf-8')
        info = tarfile.TarInfo(name=file_name)
        info.size = len(data)
        self.tar.addfile(tarinfo=info, fileobj=BytesIO(data))

    def close(self):
        self.tar.close()
