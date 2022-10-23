from pathlib import Path

import Config
from NikGapps.Helper import Constants, Git, Cmd, FileOp


class NikGapps:

    def __init__(self, android_version):
        self.android_version = str(android_version)
        self.oem = "nikgapps"
        self.repo_dir = Constants.pwd + Constants.dir_sep + f"{self.oem}_" + str(self.android_version)
        self.repo_url = f"git@gitlab.com:nikgapps/{str(self.android_version)}.git"
        self.android_dict = {}
        for v in Config.ANDROID_VERSIONS:
            self.android_dict[v] = "main"
        print(self.android_dict)
        self.branch = self.android_dict[self.android_version]
        self.tracker = "nikgapps"

    def android_version_supported(self, android_version):
        return android_version in self.android_dict

    def get_nikgapps_dict(self):
        if self.clone_gapps_image() is not None:
            return self.get_gapps_dict()
        else:
            print("Failed to clone NikGapps GApps Image")
            return None

    def clone_gapps_image(self):
        print("Cloning PixelExperience GApps Image")
        repo = Git(self.repo_dir)
        repo.clone_repo(self.repo_url, branch=self.branch, fresh_clone=False)
        return repo

    def get_gapps_dict(self):
        print("Getting NikGapps GApps Dict")
        gapps_dict = {}
        cmd = Cmd()
        for path in Path(self.repo_dir).rglob("*.apk"):
            if path.is_file() and "overlay" not in str(path):
                file_path = str(path)
                file_path = file_path[len(self.repo_dir) + 1:]
                path_split = file_path.split("/")
                appset_name = path_split[0]
                pkg_name = path_split[1]
                folder_name = path_split[2]
                supported_type = "unknown"
                if folder_name.startswith("___priv-app"):
                    supported_type = "priv-app"
                elif folder_name.startswith("___app"):
                    supported_type = "app"
                folder_name = supported_type if supported_type == "unknown" else folder_name[len(supported_type) + 6:]
                package_name = cmd.get_package_name(str(path))
                package_version = cmd.get_package_version(str(path))
                f_dict = {"partition": "system", "type": supported_type,
                          "folder": folder_name,
                          "file": file_path, "package": package_name, "version": package_version,
                          "md5": FileOp.get_md5(str(path))}
                if appset_name not in gapps_dict:
                    # the appset is new, so will be the package list
                    pkg_dict = {pkg_name: [f_dict]}
                    pkg_list = [pkg_dict]
                    gapps_dict[appset_name] = pkg_list
                else:
                    # the appset exists, so does the package list
                    tmp_pkg_list = gapps_dict[appset_name]
                    # we will go through all the packages, and check if the current package exists
                    for pkg in gapps_dict[appset_name]:
                        if pkg_name in pkg:
                            pkg[pkg_name].append(f_dict)
                        else:
                            pkg_dict = {pkg_name: [f_dict]}
                            tmp_pkg_list.append(pkg_dict)
                        break
                    gapps_dict[appset_name] = tmp_pkg_list
        return gapps_dict
