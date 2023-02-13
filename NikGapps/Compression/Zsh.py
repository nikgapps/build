import tarfile
from pathlib import Path
from subprocess import call

from NikGapps.Helper import C


class Zsh:

    def __init__(self, folder_to_compress, file_name):
        self.folder = folder_to_compress
        self.tarfile = str(file_name) + ".tar.xz"

    def compress(self):
        start_time = C.start_of_function()
        call(["tar", "cJfP", self.tarfile, self.folder])
        print(f"zsh tar filesize: {round(Path(self.tarfile).stat().st_size / (1024 * 1024), 2)} MB")
        C.end_of_function(start_time, "zsh tar filesize")
