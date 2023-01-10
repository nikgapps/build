from datetime import datetime

from NikGapps.Helper import Args, Git
from NikGapps.Git.Operations import Operations as GitOperations
from NikGapps.Helper.Json import Json
from NikGapps.OEM.Operations import Operations
from NikGapps.OEM.Rules import Rules

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
    # get the controller ready and up-to-date
    n_gapps_file = Operations.sync_tracker(oem, android_version=android_version, tracker_repo=tracker_repo)
    n_version_controller_file = Operations.update_nikgapps_controller(android_version, tracker_repo=tracker_repo,
                                                                      list_of_appsets=list_of_appsets)
    n_version_controller_dict = Json.read_dict_from_file(n_version_controller_file)
    oem_repo_dict = {oem: Operations.get_oem_repo_dir(oem, android_version=android_version)}
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
        oem_repo_dict[oem] = Operations.get_oem_repo_dir(oem, android_version=android_version)
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
            tracker_repo.update_repo_changes(f"The app versions are updated for {oem} in {android_version}")
        else:
            print(f"No update for {oem} in {android_version}")

    update_dict = {}
    for appset in n_version_controller_dict:
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
                            if int(temp_oem_version_code) > int(temp_version_code):
                                f_dict = {"oem": oem, "oem_source": file_source, "oem_version": file[f"{oem}_version"],
                                          "nikgapps_source": file["file_path"], "nikgapps_version": file["version"],
                                          "update_available": True}
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
    Operations.update_nikgapps_updater_dict(android_version=android_version, update_dict=update_dict,
                                            tracker_repo=tracker_repo)
    # execute updater
    changelog_file = Operations.get_changelog_controller(android_version=android_version, tracker_repo=tracker_repo)
    changelog_dict = Json.read_dict_from_file(changelog_file)
    updater_dict, isexists = Operations.get_updater_dict(android_version=android_version, tracker_repo=tracker_repo)
    updater_dict = Json.read_dict_from_file(updater_dict)
    changelog = {}
    for appset in updater_dict:
        print(appset)
        n_appset = Operations.get_nikgapps_appset(appset)
        Rules.update_appset(n_appset, updater_dict, oem_repo_dict, oem_tracker_dict, changelog)
    nikgapps_repo = Git(oem_repo_dict["nikgapps"])
    today = datetime.utcnow().strftime('%Y-%m-%d')
    for file in nikgapps_repo.get_changed_files():
        package_title = file.split("/")[1]
        if today not in changelog_dict:
            changelog_dict[today] = []
        if today in changelog_dict:
            package_list = changelog_dict[today]
            pkg_found = False
            for pkg in package_list:
                if package_title in pkg:
                    pkg_found = True
                    pkg[package_title] = changelog[package_title]
                    break
            if not pkg_found and package_title in changelog:
                package_list.append({package_title: changelog[package_title]})
        print(file)
    commit_message = "Google Apps updated as of " + str(today)
    if today in changelog_dict:
        package_list = changelog_dict[today]
        for pkg_dict in package_list:
            for key in pkg_dict:
                commit_message += f"\n{key}: {pkg_dict[key]}"
    Json.write_dict_to_file(changelog_dict, changelog_file)
    nikgapps_repo.update_repo_changes(f"{commit_message}")
    tracker_repo.update_repo_changes(f"{commit_message}")

