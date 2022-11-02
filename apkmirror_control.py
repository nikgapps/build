import os

from NikGapps.Git.Operations import Operations
from NikGapps.Helper.Json import Json
from NikGappsPackages import NikGappsPackages

tracker_repo = Operations.setup_tracker_repo()
if tracker_repo is None:
    print("Failed to setup tracker repo!")
    exit(1)
apk_mirror_dict_file_location = tracker_repo.working_tree_dir + os.path.sep + 'AllApkMirrorNames.json'
nikgapps_apk_mirror_map_location = tracker_repo.working_tree_dir + os.path.sep + 'nikgapps_apkmirror_map.json'
allApkMirrorNames = Json.read_dict_from_file(apk_mirror_dict_file_location)
nikgapps_package_names = {}
for appset in NikGappsPackages.get_packages("all"):
    for package in appset.package_list:
        if package.package_name is not None and package.package_name in allApkMirrorNames:
            g_dict = {"apk_mirror_package": allApkMirrorNames[package.package_name], "name": package.package_name,
                      "title": package.title, "partition": package.partition}
            nikgapps_package_names[package.package_name] = g_dict

if Json.write_dict_to_file(nikgapps_package_names, nikgapps_apk_mirror_map_location):
    print("Successfully wrote nikgapps_apkmirror_map to file!")
    tracker_repo.update_repo_changes("Updated nikgapps_apkmirror_map.json")
else:
    print("Failed to write nikgapps_apkmirror_map to file!")
    exit(1)
