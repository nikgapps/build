import os
import platform
from pathlib import Path

import pysftp
import pytz
from datetime import datetime
import Config
from Config import UPLOAD_FILES
from NikGapps.Helper import C, FileOp


class Upload:
    def __init__(self):
        self.host = "frs.sourceforge.net"
        self.username = "nikhilmenghani"
        self.password = os.environ.get('SF_PWD')
        if self.password is None or self.password.__eq__(""):
            self.password = ""
            self.sftp = None
            return
        try:
            self.sftp = pysftp.Connection(host=self.host, username=self.username, password=self.password)
        except Exception as e:
            print("Exception while connecting to SFTP: " + str(e))
            self.sftp = None
        self.release_dir = C.sourceforge_release_directory
        tz_london = pytz.timezone('Europe/London')
        datetime_london = datetime.now(tz_london)
        self.release_date = str(datetime_london.strftime("%d-%b-%Y"))

    def get_cd(self, android_version, file_type):
        folder_name = "Test"
        try:
            android_version_code = Config.ANDROID_VERSIONS[android_version]['code']
        except KeyError:
            print("Invalid Android Version")
            return self.release_dir + "/" + folder_name
        match file_type:
            case "gapps":
                folder_name = "NikGapps-" + android_version_code
            case "config":
                folder_name = "NikGapps-" + android_version_code
                return self.release_dir + "/" + folder_name
            case "addons":
                folder_name = "Addons-" + android_version_code
            case "debloater":
                folder_name = "Debloater"
            case _:
                print(file_type)
        print("Upload Dir: " + self.release_dir + "/" + folder_name)
        return self.release_dir + "/" + folder_name + "/" + self.release_date

    def upload(self, file_name, remote_directory=None):
        system_name = platform.system()
        execution_status = False
        C.telegram.message("- The zip is uploading...")
        if self.sftp is not None and system_name != "Windows" and UPLOAD_FILES:
            start_time = C.start_of_function()
            file_type = "gapps"
            if C.get_base_name(file_name).__contains__("-Addon-"):
                file_type = "addons"
            elif C.get_base_name(file_name).__contains__("Debloater"):
                file_type = "debloater"

            if remote_directory is None:
                remote_directory = self.get_cd(Config.TARGET_ANDROID_VERSION, file_type)

            remote_filename = Path(file_name).name
            try:
                self.sftp.chdir(remote_directory)
            except IOError:
                self.sftp.makedirs(remote_directory)
                self.sftp.chdir(remote_directory)
            putinfo = self.sftp.put(file_name, remote_filename)
            # print(putinfo)
            print(f'File uploaded successfully to {remote_directory}/{remote_filename}')
            download_link = C.get_download_link(file_name, remote_directory)
            print("Download Link: " + download_link)
            print("uploading file finished...")
            execution_status = True
            file_size_kb = round(FileOp.get_file_size(file_name, "KB"), 2)
            file_size_mb = round(FileOp.get_file_size(file_name), 2)
            time_taken = C.end_of_function(start_time,
                                           f"Total time taken to upload file with size {file_size_mb} MB ("
                                           f"{file_size_kb} Kb)")
            if execution_status:
                C.telegram.message(
                    f"- The zip {file_size_mb} MB uploaded in {str(round(time_taken))} seconds\n",
                    replace_last_message=True)
                if download_link is not None:
                    C.telegram.message(f"*Note:* Download link should start working in 10 minutes", escape_text=False,
                                       ur_link={f"Download": f"{download_link}"})
        else:
            print("System incompatible or upload disabled or connection failed!")
        return execution_status

    def close_connection(self):
        self.sftp.close()
        print("Connection closed")