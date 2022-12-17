# sync all the source json files
# update nikgapps controller
# run the comparison model to check if there is any update available
# if there is any update, run the approval process
from NikGapps.Helper import Args
from NikGapps.OEM.Operations import Operations
from NikGapps.Git.Operations import Operations as GitOperations
from NikGapps.OEM.Sync import Sync

list_of_supported_appsets = ["GoogleDialer"]

args = Args()
android_versions = args.get_android_versions()
tracker_repo = GitOperations.setup_tracker_repo()
if tracker_repo is None:
    print("Failed to setup tracker repo!")
    exit(1)

for android_version in android_versions:
    Operations.update_nikgapps_controller(android_version, list_of_supported_appsets, tracker_repo)
    s = Sync(list_of_supported_appsets, tracker_repo)
    list_of_oems = args.get_oems()
    s.do(android_version, list_of_supported_oems=list_of_oems)


