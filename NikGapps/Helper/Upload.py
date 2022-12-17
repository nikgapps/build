import platform

import pexpect
import time
import pytz
from datetime import datetime
import os

import Config
from Config import UPLOAD_FILES
from NikGapps.Helper import C
from NikGapps.Helper.FileOp import FileOp


class Upload:

    def __init__(self):
        upload_start_time = C.start_of_function()
        self.release_dir = C.sourceforge_release_directory
        self.sf_pwd = os.environ.get('SF_PWD')
        if self.sf_pwd is None or self.sf_pwd.__eq__(""):
            self.sf_pwd = ""
            self.successful_connection = False
            return
        tz_london = pytz.timezone('Europe/London')
        datetime_london = datetime.now(tz_london)
        self.release_date = str(datetime_london.strftime("%d-%b-%Y"))
        print("spawning sftp nikhilmenghani@frs.sourceforge.net")
        self.child = pexpect.spawn('sftp nikhilmenghani@frs.sourceforge.net')
        self.successful_connection = False
        self.day = datetime.now(pytz.timezone('Europe/London')).strftime("%a")
        print("Expecting Password")
        i = self.child.expect(["Password", "yes/no", pexpect.TIMEOUT, pexpect.EOF], timeout=120)
        if i == 2 or i == 3:
            print("Timeout has occurred, let's try one more time")
            self.child.sendcontrol('c')
            self.child = pexpect.spawn('sftp nikhilmenghani@frs.sourceforge.net')
            i = self.child.expect(["Password", "yes/no", pexpect.TIMEOUT, pexpect.EOF])
        if i == 1:
            print("sending yes")
            self.child.sendline("yes")
            print("Expecting Password")
            self.child.expect("Password")
            self.child.sendline(str(self.sf_pwd))
            print("Expecting Connected to frs.sourceforge.net or sftp> or Password")
            status = self.child.expect(["Connected to frs.sourceforge.net", "sftp> ", "Password"])
            if status == 0 or status == 1:
                self.successful_connection = True
                print("Connection was successful")
        elif i == 0:
            print("Sending Password")
            self.child.sendline(str(self.sf_pwd))
            print("Expecting Connected to frs.sourceforge.net or sftp> or Password")
            status = self.child.expect(["Connected to frs.sourceforge.net", "sftp> ", "Password"])
            if status == 0 or status == 1:
                self.successful_connection = True
                print("Connection was successful")
        else:
            print("Connection failed")
            self.child.sendline("bye")
            try:
                self.child.interact()
            except BaseException as e:
                print("Exception while interacting: " + str(e))
        C.end_of_function(upload_start_time, "Total time taken to authenticate!")

    def is_authenticated(self):
        try:
            i = self.child.expect(["sftp> ", pexpect.TIMEOUT, pexpect.EOF], timeout=3)
            if i == 0:
                print("Already Connected!")
                return True
        except Exception as e:
            print(e.args)
        return False

    def get_cd_with_date(self, android_version, file_type, input_date=None):
        if input_date is not None:
            return self.get_cd_without_date(android_version, file_type) + "/" + input_date
        else:
            return self.get_cd_without_date(android_version, file_type) + "/" + self.release_date

    def get_cd_without_date(self, android_version, file_type):
        folder_name = "Test"
        try:
            android_version_code = Config.ANDROID_VERSIONS[android_version]['code']
        except KeyError:
            print("Invalid Android Version")
            return self.release_dir + "/" + folder_name
        if file_type == "gapps" or file_type == "config":
            folder_name = "NikGapps-" + android_version_code
        elif file_type == "addons":
            folder_name = "Addons-" + android_version_code
        elif file_type == "debloater":
            folder_name = "Debloater"
        else:
            print(file_type)
        print("Upload Dir: " + self.release_dir + "/" + folder_name)
        return self.release_dir + "/" + folder_name

    def cd(self, path):
        if str(self.child.after.decode()).__eq__("Connected to frs.sourceforge.net"):
            self.child.expect("sftp> ")
        self.child.sendline("cd " + path)
        i = self.child.expect(
            ["sftp> ", "Couldn't canonicalize: No such file or directory", f"realpath {path}: No such file"])
        if i == 0:
            return True
        elif i in (1, 2):
            return False

    def make_folder(self, android_version, file_type, folder_name=None):
        self.cd(self.get_cd_without_date(android_version, file_type))
        if folder_name is not None:
            print("Creating " + folder_name)
            self.child.sendline("mkdir " + folder_name)
        else:
            print("Creating " + self.release_date)
            self.child.sendline("mkdir " + self.release_date)
        time.sleep(1)

    def upload_file(self, file_path):
        self.child.sendline("put " + file_path)
        self.child.expect("Uploading")
        self.child.expect("100%", timeout=3600)
        self.child.expect("sftp>")
        time.sleep(1)

    def upload(self, file_name):
        system_name = platform.system()
        execution_status = False
        C.telegram.message("- The zip is uploading...")
        download_link = None
        if system_name != "Windows" and UPLOAD_FILES:
            start_time = C.start_of_function()
            # make the connection and initialize the parameters
            file_type = "gapps"
            if C.get_base_name(file_name).__contains__("Addon"):
                file_type = "addons"
            elif C.get_base_name(file_name).__contains__("Debloater"):
                file_type = "debloater"
            # proceed only if the connection is successful
            if self.successful_connection:
                # check if directory exists, if it does, we're good to upload the file
                cd = self.get_cd_with_date(Config.TARGET_ANDROID_VERSION, file_type)
                print(f"Checking if {cd} exists")
                dir_exists = self.cd(cd)
                if not dir_exists:
                    print(str(cd) + " doesn't exist!")
                    # make the folder with current date if the directory doesn't exist
                    self.make_folder(Config.TARGET_ANDROID_VERSION, file_type)
                    # try to cd again
                    dir_exists = self.cd(cd)
                # if the directory exists, we can upload the file
                if dir_exists:
                    print("uploading " + file_name + f" to {cd}...")
                    self.upload_file(file_name)
                    download_link = C.get_download_link(file_name, cd)
                    print("Download Link: " + download_link)
                    print("uploading file finished...")
                    execution_status = True
                else:
                    print("The directory doesn't exist!")
            else:
                print("The Connection Failed!")
            file_size_kb = round(FileOp.get_file_size(file_name, "KB"), 2)
            file_size_mb = round(FileOp.get_file_size(file_name), 2)
            time_taken = C.end_of_function(start_time,
                                           f"Total time taken to upload file with size {file_size_mb} MB ("
                                           f"{file_size_kb} Kb)")
            if execution_status:
                C.telegram.message(
                    f"- The zip {file_size_mb} MB ({file_size_kb} Kb) uploaded in {str(round(time_taken))} seconds\n",
                    replace_last_message=True)
                if download_link is not None:
                    C.telegram.message(f"[Download]({download_link})\n", escape_text=False)
                    C.telegram.message(f"Note:- Download link should start working in 10 minutes")
        else:
            print("System incompatible or upload disabled!")
        return execution_status

    def close(self):
        if not str(self.sf_pwd).__eq__(""):
            self.child.sendline("bye")
            self.child.close()
