from pathlib import Path

from NikGapps.Helper import Constants, Cmd, FileOp, Git


class PixelExperience:
    def __init__(self, android_version):
        self.android_version = str(android_version)
        self.oem = "pe_gapps"
        self.repo_dir = Constants.pwd + Constants.dir_sep + f"{self.oem}_" + str(self.android_version)
        self.repo_url = "git@gitlab.com:PixelExperience/thirteen/vendor_gapps.git"
        self.android_dict = {"13": "thirteen"}
        self.branch = self.android_dict[self.android_version]
        self.tracker = "pixel_experience"

    def android_version_supported(self, android_version):
        return android_version in self.android_dict

    def get_pixel_experience_dict(self):
        if self.clone_gapps_image() is not None:
            return self.get_gapps_dict()
        else:
            print("Failed to clone PixelExperience GApps Image")
            return None

    def clone_gapps_image(self):
        print("Cloning PixelExperience GApps Image")
        repo = Git(self.repo_dir)
        repo.clone_repo(self.repo_url, branch=self.branch, fresh_clone=False)
        return repo

    def get_gapps_dict(self):
        print("Getting PixelExperience GApps Dict")
        supported_partitions = ["system", "system_ext", "product", "vendor"]
        gapps_dict = {}
        cmd = Cmd()
        for partition in supported_partitions:
            supported_types = {"privileged_apps": "priv-app", "apps": "app"}
            for supported_type in supported_types:
                partition_dir = self.repo_dir + Constants.dir_sep + partition + Constants.dir_sep + \
                                "packages" + Constants.dir_sep + supported_type + Constants.dir_sep
                for path in Path(partition_dir).rglob("*.apk"):
                    if path.is_file():
                        file_path = str(path)
                        file_path = file_path[len(partition_dir):]
                        folder_name = file_path.split("/")[0]
                        package_name = cmd.get_package_name(str(path))
                        package_version = cmd.get_package_version(str(path))
                        gapps_list = []
                        g_dict = {"partition": partition, "type": supported_types[supported_type],
                                  "folder": folder_name,
                                  "file": file_path, "package": package_name, "version": package_version,
                                  "md5": FileOp.get_md5(str(path))}
                        if folder_name in gapps_dict:
                            gapps_list = gapps_dict[folder_name]
                            gapps_list.append(g_dict)
                        else:
                            gapps_list.append(g_dict)
                            gapps_dict[folder_name] = gapps_list
        return gapps_dict