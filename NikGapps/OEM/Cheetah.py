from pathlib import Path

from bs4 import BeautifulSoup

from NikGapps.Helper import Git, C, FileOp, Cmd
from NikGapps.OEM.AndroidDump import AndroidDump
from NikGapps.Web.Requests import Requests


class Cheetah(AndroidDump):
    def __init__(self, android_version, gapps_dict=None):
        super().__init__()
        self.oem = "cheetah"
        self.oem = self.oem.lower()
        self.url = self.host + self.oem
        self.repo_dir = C.pwd + C.dir_sep + f"{self.oem}_" + str(android_version)
        self.gapps_dict = {} if gapps_dict is None else gapps_dict
        self.branch = self.get_latest_branch()

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

    def get_repo_dir(self):
        return self.repo_dir

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
        self.gapps_dict = {"branch": self.branch}
        cmd = Cmd()
        for partition in supported_partitions:
            supported_types = {"priv-app": "priv-app", "app": "app"}
            for supported_type in supported_types:
                partition_dir = self.repo_dir + C.dir_sep + partition + C.dir_sep + \
                                supported_type + C.dir_sep
                for path in Path(partition_dir).rglob("*.apk"):
                    if path.is_file():
                        file_path = str(path)
                        file_location = file_path[len(self.repo_dir) + 1:]
                        file_path = file_path[len(partition_dir):]
                        folder_name = file_path.split("/")[0]
                        package_name = cmd.get_package_name(str(path))
                        package_version = cmd.get_package_version(str(path))
                        version = ''.join([i for i in package_version if i.isdigit()])
                        gapps_list = []
                        g_dict = {"partition": partition, "type": supported_types[supported_type],
                                  "folder": folder_name, "version_code": version,
                                  "file": file_path, "package": package_name, "version": package_version,
                                  "location": file_location}
                        if package_name in self.gapps_dict:
                            gapps_list = self.gapps_dict[package_name]
                            gapps_list.append(g_dict)
                        else:
                            gapps_list.append(g_dict)
                            self.gapps_dict[package_name] = gapps_list
        return self.gapps_dict

    def get_file_list_dict(self, pkg):
        oem_file_list_dict = {}
        folder = None
        file_list = []
        # get the folder from the package as pkg is of primary apk, so that folder counts
        for oem_pkg in self.gapps_dict:
            if str(pkg).__eq__(str(oem_pkg)) and folder is None:
                for oem_file in self.gapps_dict[oem_pkg]:
                    folder = str(oem_file["folder"])
                    break
        if folder is not None:
            for oem_pkg in self.gapps_dict:
                if str(oem_pkg).__eq__("branch"):
                    continue
                for oem_file in self.gapps_dict[oem_pkg]:
                    if str(folder).__eq__(str(oem_file["folder"])):
                        f_dict = {"partition": oem_file["partition"], "type": oem_file["type"],
                                  "folder": folder, "package": oem_file["package"],
                                  "file": oem_file["file"], "version_code": oem_file["version_code"],
                                  "version": oem_file["version"], "location": oem_file["location"]}
                        file_list.append(f_dict)
        if len(file_list) > 0:
            oem_file_list_dict[pkg] = file_list
        return oem_file_list_dict
