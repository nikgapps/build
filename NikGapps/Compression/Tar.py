import tarfile
from pathlib import Path

from NikGapps.Helper import C


class Tar:

    def __init__(self, folder_to_compress, file_name):
        self.folder = folder_to_compress
        self.tarfile = str(file_name) + ".tar.xz"

    def compress(self):
        start_time = C.start_of_function()
        with tarfile.open(self.tarfile, "w:xz") as tar:
            tar.add(self.folder, arcname=self.folder.stem)
        print(f"py tar filesize: {round(Path(self.tarfile).stat().st_size / (1024 * 1024), 2)} MB")
        C.end_of_function(start_time, "py tar filesize")
