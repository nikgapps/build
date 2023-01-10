import os
from pathlib import Path

from NikGapps.Helper import FileOp, C
from NikGapps.Helper.Json import Json
from NikGapps.OEM.Operations import Operations


class Rules:

    @staticmethod
    def update_package(n_package, oem, n_appset_title, oem_repo_dict, oem_tracker_dict):
        oem_repo = oem_repo_dict[oem]
        oem_dict = Json.read_dict_from_file(oem_tracker_dict[oem])
        oem_files = Operations.get_oem_file_list_dict(n_package.package_name, oem_dict)
        nikgapps_repo = oem_repo_dict["nikgapps"]
        working_dir = os.path.join(nikgapps_repo, n_appset_title, n_package.package_title)
        folders_to_delete = []
        changelog = {}
        # operation on nikgapps
        for file in Path(working_dir).rglob("*.apk*"):
            if str(file).__contains__("overlay"):
                continue
            file_parent = str(file.parent)
            folder = file_parent[len(working_dir) + 1:].split("/")[0]
            folder_with_apk = str(working_dir) + "/" + folder
            folders_to_delete.append(folder_with_apk)
        for folder in folders_to_delete:
            print("Deleting folder: " + folder)
            FileOp.remove_dir(folder)
        # operation on oem
        for file in oem_files[n_package.package_name]:
            file_path = Path(file["file"])
            location = file["location"]
            source = os.path.join(oem_repo, location)
            output = str("/" + file["type"] + "/" + str(file_path.parent)).replace("/", "___")
            destination = os.path.join(working_dir, output, str(file_path.name))
            print(source)
            print(destination)
            FileOp.copy_file(source, destination)
            if file["package"] == n_package.package_name:
                changelog[n_package.package_title] = file["version"]
            print("")
        return changelog

    @staticmethod
    def update_appset(n_appset, updater_dict, oem_repo_dict, oem_tracker_dict, changelog_dict):
        for packages in updater_dict[n_appset.title]:
            for package in packages:
                print(package)
                # all the files have update flag, so we can check the first file before performing any operations
                update_available = False
                for file in packages[package]:
                    if file["update_available"]:
                        update_available = True
                    else:
                        C.print_yellow(f"No update available for {package}")
                    break
                if update_available:
                    n_package = Operations.get_nikgapps_package(n_appset, package)
                    oem = packages[package][0]["oem"]
                    if n_package is None:
                        print(f"Failed to get nikgapps package for {package}")
                        continue
                    match package:
                        case _:
                            changelog = Rules.update_package(n_package, oem, n_appset.title, oem_repo_dict,
                                                             oem_tracker_dict)
                    changelog_dict[n_package.package_title] = changelog[n_package.package_title]
