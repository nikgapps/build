from pathlib import Path

from NikGapps.Helper import C, Cmd, FileOp, Git


class EvoX:

    def __init__(self, android_version):
        self.android_version = str(android_version)
        self.oem = "EvoX"
        self.oem = self.oem.lower()
        self.repo_dir = C.pwd + C.dir_sep + f"{self.oem}_" + str(self.android_version)
        self.android_dict = {"13": "tiramisu"}
        self.branch = self.android_dict[self.android_version]
        self.repo_url = f"https://gitlab.com/{self.oem}/vendor_gms.git"
        self.tracker = self.oem
        self.is_supported = self.android_version_supported(self.android_version)

    def android_version_supported(self, android_version):
        return android_version in self.android_dict

    def get_repo_dir(self):
        return self.repo_dir

    def get_evo_x_dict(self):
        if self.clone_gapps_image() is not None:
            return self.get_gapps_dict()
        else:
            print(f"Failed to clone {self.oem} GApps Image")
            return None

    def clone_gapps_image(self):
        print(f"Cloning {self.oem} GApps Image")
        repo = Git(self.repo_dir)
        result = repo.clone_repo(self.repo_url, branch=self.branch, fresh_clone=False)
        return repo if result else None

    def get_gapps_dict(self):
        print(f"Getting {self.oem} GApps Dict")
        supported_partitions = ["system", "system_ext", "product", "vendor"]
        gapps_dict = {}
        cmd = Cmd()
        for partition in supported_partitions:
            supported_types = {"privileged_apps": "priv-app", "apps": "app"}
            for supported_type in supported_types:
                partition_dir = self.repo_dir + C.dir_sep + partition + C.dir_sep + \
                                "packages" + C.dir_sep + supported_type + C.dir_sep
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
                        if package_name in gapps_dict:
                            gapps_list = gapps_dict[package_name]
                            gapps_list.append(g_dict)
                        else:
                            gapps_list.append(g_dict)
                            gapps_dict[package_name] = gapps_list
        return gapps_dict

