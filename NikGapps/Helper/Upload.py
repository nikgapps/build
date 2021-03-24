import pexpect
import time
import pytz
from datetime import datetime
import Config
import os


class Upload:

    def __init__(self):
        self.release_dir = "/home/frs/project/nikgapps/Releases"
        sf_pwd = os.environ.get('SF_PWD')
        if sf_pwd is None:
            sf_pwd = ""
        tz_london = pytz.timezone('Europe/London')
        datetime_london = datetime.now(tz_london)
        self.release_date = str(datetime_london.strftime("%d-%b-%Y"))
        self.child = pexpect.spawn('sftp nikhilmenghani@frs.sourceforge.net')
        self.successful_connection = False
        self.day = datetime.now(pytz.timezone('Europe/London')).strftime("%a")
        i = self.child.expect(["Password", "yes/no"])
        if i == 1:
            self.child.sendline("yes")
            self.child.expect("Password")
            self.child.sendline(str(sf_pwd))
            status = self.child.expect(["Connected to frs.sourceforge.net", "sftp> ", "Password"])
            if status == 0 or status == 1:
                self.successful_connection = True
                print("Connection was successful")
        elif i == 0:
            self.child.sendline(str(sf_pwd))
            status = self.child.expect(["Connected to frs.sourceforge.net", "sftp> ", "Password"])
            if status == 0 or status == 1:
                self.successful_connection = True
                print("Connection was successful")
        else:
            print("Connection failed")
            self.child.sendline("bye")
            self.child.interact()

    def get_cd_with_date(self, android_version, file_type, input_date=None):
        if input_date is not None:
            return self.get_cd_without_date(android_version, file_type) + "/" + input_date
        else:
            return self.get_cd_without_date(android_version, file_type) + "/" + self.release_date

    def get_cd_without_date(self, android_version, file_type):
        folder_name = "Test"
        if file_type == "gapps":
            if android_version == 9:
                folder_name = "NikGapps-P"
            elif android_version == 10:
                folder_name = "NikGapps-Q"
            elif android_version == 11:
                folder_name = "NikGapps-R"
        elif file_type == "addons":
            if android_version == 9:
                folder_name = "Addons-P"
            elif android_version == 10:
                folder_name = "Addons-Q"
            elif android_version == 11:
                folder_name = "Addons-R"
        elif file_type == "debloater":
            folder_name = "Debloater"
        if self.day != Config.RELEASE_DAY:
            return "/home/frs/project/nikgapps/Canary-Releases" + "/" + folder_name
        return self.release_dir + "/" + folder_name

    def cd(self, path):
        self.child.expect("sftp> ")
        self.child.sendline("cd " + path)
        i = self.child.expect(["sftp> ", "Couldn't canonicalize: No such file or directory"])
        if i == 0:
            return True
        elif i == 1:
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

    def close(self):
        self.child.sendline("bye")
        self.child.close()
