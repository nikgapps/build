from pathlib import Path

from bs4 import BeautifulSoup

from NikGapps.Helper import Git, C, FileOp, Cmd
from NikGapps.OEM.AndroidDump import AndroidDump
from NikGapps.Web.Requests import Requests


class Cheetah(AndroidDump):
    def __init__(self, android_version):
        super().__init__()
        self.oem = "cheetah"
        self.oem = self.oem.lower()
        self.url = self.host + self.oem
        self.repo_dir = C.pwd + C.dir_sep + f"{self.oem}_" + str(android_version)
        self.branch = "cheetah-user-13-TQ1A.221205.011-9244662-release-keys"

    def get_latest_branch(self):
        page_response = Requests.get(self.url + "/-/branches", headers=self.header)
        if page_response.status_code != 200:
            print(f"Error getting latest branch for {self.oem}, failed with status code {page_response.status_code}")
            return None
        page_text = page_response.text
        soup = BeautifulSoup(page_text, features="html.parser")
        for content in soup.select('.content-list.all-branches'):
            for link in content.find_all('a'):
                if str(link['href']).startswith(f'/dumps/google/{self.oem}/'):
                    return link.text.strip()

    def clone_gapps_image(self):
        print(f"Cloning {self.oem} GApps Image")
        if self.branch is None:
            self.branch = self.get_latest_branch()
        repo_url = self.url + ".git"
        repo = Git(self.repo_dir)
        result = repo.clone_repo(repo_url, branch=self.branch, fresh_clone=False)
        return repo if result else None

    def get_gapps_dict(self):
        print(f"Getting {self.oem} GApps Dict")
        if self.clone_gapps_image() is not None:
            return self.get_android_dump_dict()
        else:
            print(f"Failed to clone {self.oem} GApps Image")
            return None

    def get_android_dump_dict(self):
        supported_partitions = ["system", "system_ext", "product", "vendor"]
        gapps_dict = {}
        cmd = Cmd()
        for partition in supported_partitions:
            supported_types = {"priv-app": "priv-app", "app": "app"}
            for supported_type in supported_types:
                partition_dir = self.repo_dir + C.dir_sep + partition + C.dir_sep + \
                                supported_type + C.dir_sep
                for path in Path(partition_dir).rglob("*.apk"):
                    if path.is_file():
                        file_path = str(path)
                        file_path = file_path[len(partition_dir):]
                        folder_name = file_path.split("/")[0]
                        package_name = cmd.get_package_name(str(path))
                        package_version = cmd.get_package_version(str(path))
                        version = ''.join([i for i in package_version if i.isdigit()])
                        gapps_list = []
                        g_dict = {"partition": partition, "type": supported_types[supported_type],
                                  "folder": folder_name, "version_code": version,
                                  "file": file_path, "package": package_name, "version": package_version,
                                  "md5": FileOp.get_md5(str(path))}
                        if package_name in gapps_dict:
                            gapps_list = gapps_dict[package_name]
                            gapps_list.append(g_dict)
                        else:
                            gapps_list.append(g_dict)
                            gapps_dict[package_name] = gapps_list
        return gapps_dict
