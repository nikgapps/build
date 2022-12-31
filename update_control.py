from NikGapps.Helper import Args
from NikGapps.Helper.Json import Json
from NikGapps.OEM.Operations import Operations
from NikGapps.Git.Operations import Operations as GitOperations
from NikGapps.OEM.Sync import Sync

list_of_supported_appsets = ["Core"]
update_all_oems = True
args = Args()
android_versions = args.get_android_versions()
tracker_repo = GitOperations.setup_tracker_repo()
if tracker_repo is None:
    print("Failed to setup tracker repo!")
    exit(1)
list_of_oems = args.get_oems()
for android_version in android_versions:
    # update the controller with nikgapps apps, we want to make sure if the updates in the source are captured
    Operations.update_nikgapps_controller(android_version, list_of_supported_appsets, tracker_repo)
    s = Sync(list_of_supported_appsets, tracker_repo)
    s.do(android_version, list_of_supported_oems=list_of_oems)

for android_version in android_versions:
    # get the dictionary file which can be used to filter the oems we want to check
    controller_dict_file = Operations.get_oems_from_controller(android_version,
                                                               tracker_repo, return_file=True)
    if controller_dict_file is None:
        print(f"Failed to get controller file for {android_version}")
        continue
    controller_dict = Json.read_dict_from_file(controller_dict_file)
    # supported oems are the distinct oems found in the controller
    # controller_appsets are the appsets found in the controller
    supported_oems, controller_appsets = Operations.get_oems_from_controller_dict(controller_dict)
    for oem in list_of_oems:
        if oem not in supported_oems:
            supported_oems.append(oem)
    for oem in supported_oems:
        # get specific appsets for the oem (if update_all_oems is False)
        appset_oem_dict = Operations.get_appsets_from_controller_dict(controller_dict,
                                                                      filter_oem=None if update_all_oems else oem)
        # get the tracker file for the oem
        tracker_file_dict = Operations.get_tracker_dict(android_version=android_version, oem=oem,
                                                        tracker_repo=tracker_repo)
        # update the controller with oem details
        if Operations.update_nikgapps_controller_version(controller_dict_file=controller_dict_file,
                                                         appset_dict=appset_oem_dict, oem_dict=tracker_file_dict,
                                                         oem=oem):
            print(f"Updated controller for {oem} in {android_version}")
            tracker_repo.update_repo_changes(f"The app versions are updated for {oem} in {android_version}")
        else:
            print(f"No update for {oem} in {android_version}")

for android_version in android_versions:
    controller_dict_file = Operations.get_oems_from_controller(android_version,
                                                               tracker_repo, return_file=True)
    if controller_dict_file is None:
        print(f"Failed to get controller file for {android_version}")
        continue
    controller_dict = Json.read_dict_from_file(controller_dict_file)
    for appset in controller_dict:
        for packages in controller_dict[appset]:
            for package in packages:
                print(package)
                for file in packages[package]:
                    update_indicator = file["update_indicator"]
                    oem = file["update_source"]
                    version_code = file["version_code"]
                    if f"{oem}_version_code" in file:
                        oem_version_code = file[f"{oem}_version_code"]
                        len_of_oem_version_code = len(oem_version_code)
                        len_of_version_code = len(version_code)
                        temp_oem_version_code = oem_version_code
                        temp_version_code = version_code
                        if len_of_oem_version_code > 6:
                            temp_oem_version_code = oem_version_code[:int(len_of_oem_version_code/2)]
                            temp_version_code = version_code[:int(len_of_oem_version_code/2)]
                        if int(temp_oem_version_code) > int(temp_version_code):
                            print(f"Update available for {package} in {appset} in {android_version}")
                        else:
                            print(f"No update available for {package} in {appset} in {android_version}")
                    else:
                        print(f"No update code found for {package} in {appset} in {android_version}")
