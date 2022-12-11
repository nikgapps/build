import os

import Config
from NikGapps.Config.NikGappsConfig import NikGappsConfig
from NikGapps.Git.PullRequest import PullRequest
import re

from NikGapps.Web.Requests import Requests


class Validate:

    @staticmethod
    def pull_request(pr: PullRequest):
        failure_reason = []
        files_changed = pr.files_changed
        total = len(files_changed)
        regex = '[^a-zA-Z0-9_-]'
        print("Total files changed: " + str(total))
        for i in range(0, total):
            print("-------------------------------------------------------------------------------------")
            file_name = str(files_changed[i]["filename"])
            download_url = str(files_changed[i]["raw_url"])
            raw_nikgapps_config = Requests.get_text(download_url)
            raw_file_name = os.path.splitext((os.path.basename(file_name)))[0]
            print("Validating: " + file_name)
            print("-------------------------------------------------------------------------------------")
            print("- checking file name: " + raw_file_name)
            if file_name.__contains__("#") or file_name.__contains__("!"):
                failure_reason.append(f"{file_name} contains symbols in the name which are not allowed. "
                                      f"Only alphanumeric names are allowed!")
            if not file_name.endswith(".config"):
                failure_reason.append(f"{file_name} doesn't have .config extension, we only accept config files!")
            print("- checking if android version is present")
            config_android_version = ""
            for android_version in Config.ANDROID_VERSIONS:
                if str(file_name).startswith(android_version + os.path.sep):
                    config_android_version = android_version
            if config_android_version.__eq__(""):
                if file_name.startswith("archive" + os.path.sep):
                    failure_reason.append(f"You cannot modify archived file {file_name}")
                else:
                    failure_reason.append(f"{file_name} must be part of Android Version folder, not outside of it!")
            print("- checking if filename is alphanumeric")
            regex_match = re.search(regex, raw_file_name)
            if regex_match is not None:
                failure_reason.append(
                    f"{file_name} is not an aphanumeric name, "
                    f"make sure the name of config file is between A-Z and 0-9 "
                    f"additionally, accepted symbols are - (dash) or _ (underscore) "
                    f"any symbols including but not limited to (, ' . # ! *) or space are not accepted in the name "
                    f"try renaming the file to a name that doesn't contain any spaces or special characters")
                print(regex_match)
            print("- checking file status")
            file_status = str(files_changed[i]["status"])
            if not file_status.__eq__("added"):
                failure_reason.append(
                    f"Cannot merge the changes automatically since {file_name} is either modified or removed, "
                    "Wait for someone to manually review!")
            print("- checking version compatibility")
            for line in raw_nikgapps_config.splitlines():
                if line.startswith("Version="):
                    version = line.split("=")[1]
                    config_obj = NikGappsConfig()
                    if not version.__eq__(str(config_obj.config_version)):
                        failure_reason.append(
                            f"{file_name} is on version {version} which is not the latest version of NikGapps Config, "
                            f"please update the config file to version {config_obj.config_version}")
                    break

        return failure_reason
