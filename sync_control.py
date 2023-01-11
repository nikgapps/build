
from NikGapps.Helper import Args
from NikGapps.Git.Operations import Operations as GitOperations
from NikGapps.OEM.Operations import Operations

args = Args()
android_versions = args.get_android_versions()
list_of_oems = args.get_oems()
tracker_repo = GitOperations.setup_tracker_repo()
for android_version in android_versions:
    for oem in list_of_oems:
        oem_tracker_file = Operations.sync_tracker(android_version=android_version, oem=oem, appsets=None,
                                                   tracker_repo=tracker_repo)
