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
            if file_name.__contains__("Addon"):
                failure_reason.append(f"{file_name} contains Addon in the name, please avoid using Addon in the name. "
                                      f"It conflicts with the official Addon naming convention!")
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
                    f"Cannot merge the changes automatically since status of {file_name} is {file_status}, "
                    "kindly start fresh with forking the repository again!")
            print("- checking version compatibility")
            config_obj = NikGappsConfig(raw_config=raw_nikgapps_config)
            if "Version" in config_obj.config_dict:
                version = config_obj.config_dict["Version"]
                if not version.__eq__(str(config_obj.config_version)):
                    failure_reason.append(
                        f"{file_name} is on version {version} which is not the latest version of NikGapps Config, "
                        f"please update the config file to version {config_obj.config_version}")
            else:
                failure_reason.append(
                    f"{file_name} is missing version information, please use latest version of NikGapps Config "
                    f"i.e. {config_obj.config_version}")
            core_enabled = False
            core_go_enabled = False
            for appset in config_obj.config_package_list:
                match str(appset.title).lower():
                    case "googlechrome":
                        enabled_pkg_count = len(appset.package_list)
                        if enabled_pkg_count < 3:
                            failure_reason.append(f"Update {file_name}, "
                                                  "All the packages under Google Chrome needs to be enabled, "
                                                  "you cannot disable any of the packages under Google Chrome.\n"
                                                  "Either enable all or disable all.")
                    case "core":
                        core_enabled = True
                    case "corego":
                        core_go_enabled = True
            if core_enabled and core_go_enabled:
                failure_reason.append(f"Update {file_name}, "
                                      "You cannot enable both Core and Core Go, you can only enable one of them")
        return failure_reason
