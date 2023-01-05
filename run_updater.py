import os
from pathlib import Path

from NikGapps.Helper import Args, C, FileOp, Git
from NikGapps.Git.Operations import Operations as GitOperations
from NikGapps.Helper.Json import Json
from NikGapps.OEM.Operations import Operations

list_of_appsets = ["Core"]
update_all_oems = True
args = Args()
android_versions = args.get_android_versions()
tracker_repo = GitOperations.setup_tracker_repo()

if tracker_repo is None:
    print("Failed to setup tracker repo!")
    exit(1)

list_of_oems = args.get_oems()

for android_version in android_versions:
    oem = "nikgapps"
    n_gapps_file = Operations.sync_tracker(oem, android_version=android_version, tracker_repo=tracker_repo)
    n_version_controller_file = Operations.update_nikgapps_controller(android_version, tracker_repo=tracker_repo,
                                                                      list_of_appsets=list_of_appsets)
    n_version_controller_dict = Json.read_dict_from_file(n_version_controller_file)
    oem_dict = {oem: Operations.get_oem_repo_dir(oem, android_version=android_version)}
    oem_tracker_dict = {oem: n_gapps_file}
    controller_oems, controller_appsets = Operations.get_oems_from_controller_dict(n_version_controller_dict)
    for oem in controller_oems:
        if oem not in list_of_oems:
            list_of_oems.append(oem)
    for appset in controller_appsets:
        if appset not in list_of_appsets:
            list_of_appsets.append(appset)

    for oem in list_of_oems:
        oem_tracker_file = Operations.sync_tracker(android_version=android_version, oem=oem, appsets=list_of_appsets,
                                                   tracker_repo=tracker_repo)
        oem_dict[oem] = Operations.get_oem_repo_dir(oem, android_version=android_version)
        oem_tracker_dict[oem] = oem_tracker_file
        # get specific appsets for the oem (if update_all_oems is False)
        appset_oem_dict = Operations.get_appsets_from_controller_dict(n_version_controller_dict,
                                                                      filter_oem=None if update_all_oems else oem)
        tracker_file_dict = Json.read_dict_from_file(oem_tracker_dict[oem])
        # update the controller with oem details
        if Operations.update_nikgapps_controller_version(controller_dict_file=n_version_controller_file,
                                                         appset_dict=appset_oem_dict, oem_dict=tracker_file_dict,
                                                         oem=oem):
            print(f"Updating controller for {oem} in {android_version}")
            # tracker_repo.update_repo_changes(f"The app versions are updated for {oem} in {android_version}")
        else:
            print(f"No update for {oem} in {android_version}")

    for appset in n_version_controller_dict:
        update_dict = {}
        for packages in n_version_controller_dict[appset]:
            for package in packages:
                for file in packages[package]:
                    if file["update_indicator"] == "1":
                        oem = file["update_source"]
                        version_code = file["version_code"]
                        if f"{oem}_version_code" in file:
                            oem_version_code = file[f"{oem}_version_code"]
                            file_source = file[f"{oem}_location"]
                            len_of_oem_version_code = len(oem_version_code)
                            temp_oem_version_code = oem_version_code[:int(
                                len_of_oem_version_code / 2)] if len_of_oem_version_code > 6 else oem_version_code
                            temp_version_code = version_code[:int(
                                len_of_oem_version_code / 2)] if len_of_oem_version_code > 6 else version_code
                            update_available = False
                            if int(temp_oem_version_code) > int(temp_version_code):
                                update_available = True
                            f_dict = {"oem": oem, "oem_source": file_source, "oem_version": file[f"{oem}_version"],
                                      "nikgapps_source": file["file_path"], "nikgapps_version": file["version"],
                                      "update_available": update_available}
                            if appset not in update_dict:
                                # the appset is new, so will be the package list
                                pkg_dict = {package: [f_dict]}
                                pkg_list = [pkg_dict]
                                update_dict[appset] = pkg_list
                            else:
                                pkg_list = update_dict[appset]
                                pkg_found = False
                                for pkg_dict in pkg_list:
                                    if package in pkg_dict:
                                        pkg_dict[package].append(f_dict)
                                        pkg_found = True
                                        break
                                if not pkg_found:
                                    pkg_dict = {package: [f_dict]}
                                    pkg_list.append(pkg_dict)
    # execute updater
    updater_dict, isexists = Operations.get_updater_dict(android_version=android_version, tracker_repo=tracker_repo)
    updater_dict = Json.read_dict_from_file(updater_dict)
    for appset in updater_dict:
        print(appset)
        n_appset = Operations.get_nikgapps_appset(appset)
        for packages in updater_dict[appset]:
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
                    # remove the folder that has apk in it and skip the overlay
                    # before we delete, we need to run the rules to check if we have enough files to replace
                    if n_package is None:
                        print(f"Failed to get nikgapps package for {package}")
                        continue
                    # usually we will only have one file, but we will loop through all the files for consistency
                    # we will run a few rules before we delete the files
                    # we are here because we had at least one file to update, so we can fetch oem from first file
                    oem = packages[package][0]["oem"]
                    oem_repo = oem_dict[oem]
                    nikgapps_repo = oem_dict["nikgapps"]
                    working_dir = os.path.join(nikgapps_repo, n_appset.title, n_package.package_title)
                    file_count = 0
                    folders_to_delete = []
                    files_to_delete = []
                    for file in Path(working_dir).rglob("*.apk"):
                        if str(file).__contains__("overlay"):
                            continue
                        file_count += 1
                        folders_to_delete.append(str(file.parent))
                        files_to_delete.append(str(file))
                    if file_count == 1 and len(packages[package]) == 1:
                        # encountered a common scenario, so we will delete the file and copy the new file
                        for file in files_to_delete:
                            FileOp.remove_file(file)
                            print(f"Removed {file}")
                    # rules finished, now time to copy the files
                    for file in packages[package]:
                        oem_source = file["oem_source"]
                        nikgapps_source = file["nikgapps_source"]
                        source = os.path.join(oem_repo, oem_source)
                        destination = os.path.join(nikgapps_repo, n_appset.title, n_package.package_title,
                                                   nikgapps_source)
                        FileOp.copy_file(source, destination)
    nikgapps_repo = Git(oem_dict["nikgapps"])
    nikgapps_repo.update_repo_changes(f"Updated {android_version} app versions")
    print(oem_dict)
    print(oem_tracker_dict)
