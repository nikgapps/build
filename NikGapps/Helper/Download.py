import wget

from NikGapps.Helper.FileOp import FileOp


class Download:

    @staticmethod
    def from_url(url, location_in_cwd):
        print(f'Downloading from {url}...')
        if FileOp.file_exists(location_in_cwd):
            FileOp.remove_file(location_in_cwd)
        FileOp.create_file_dir(location_in_cwd)
        try:
            file_name = wget.download(url, location_in_cwd)
            if str(file_name).__eq__(location_in_cwd):
                print("File " + location_in_cwd + " successfully downloaded")
            else:
                print("Something went wrong while downloading file " + location_in_cwd)
                return False
        except Exception as e:
            print("Exception occurred: " + str(e) + " while downloading")
            return False
        if FileOp.file_exists(location_in_cwd):
            return True
        else:
            print("Failed to download file " + location_in_cwd)
            return False
