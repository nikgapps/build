import argparse

from NikGapps.Helper.B64 import B64


class Args:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            description="NikGapps build command help!")
        parser.add_argument(
            '-U', '--userID', help="Telegram User Id", default='-1', type=str)
        parser.add_argument(
            '-C', '--config', help="byte64 value of nikgapps.config", type=str)
        parser.add_argument(
            '-G', '--enableGitCheck', help="Include this to enable git operations", action="store_true")
        parser.add_argument(
            '-A', '--androidVersion', help="It is the android version for which we need to build the gapps",
            default="-1",
            type=str)
        parser.add_argument(
            '-P', '--packageList', help="List of packages to build", type=str)

        args = parser.parse_args()

        self.user_id = args.userID
        self.config_value = args.config
        self.enable_git_check = args.enableGitCheck
        self.android_version = args.androidVersion
        self.package_list = args.packageList

    def get_package_list(self):
        if self.config_value is None and self.package_list is not None:
            pkg_list = self.package_list.split(',')
        elif self.config_value is not None:
            # generate from config
            config_string = B64.b64d(self.config_value)
            pkg_list = self.package_list.split(',')
        else:
            pkg_list = []
        return pkg_list

    def get_android_versions(self):
        if self.android_version is not None:
            android_versions = self.android_version.split(',')
        else:
            android_versions = []
        return android_versions
