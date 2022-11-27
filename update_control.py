# sync all the source json files
# update nikgapps controller
# run the comparison model to check if there is any update available
# if there is any update, run the approval process
from NikGapps.Helper import Args
from NikGapps.OEM.Operations import Operations
from NikGapps.Git.Operations import Operations as GitOperations

list_of_supported_appsets = ["GoogleDialer"]

args = Args()
android_versions = args.get_android_versions()
tracker_repo = GitOperations.setup_tracker_repo()
if tracker_repo is None:
    print("Failed to setup tracker repo!")
    exit(1)
for android_version in android_versions:
    list_of_supported_oems = Operations.get_oems_from_controller(android_version, tracker_repo)
    for oem in list_of_supported_oems:
        Operations.sync_tracker(android_version=android_version, oem=oem, tracker_repo=tracker_repo)
    Operations.sync_with_nikgapps_tracker(android_version, tracker_repo)
    Operations.update_nikgapps_controller(android_version, list_of_supported_appsets, tracker_repo)
    print(android_version)

