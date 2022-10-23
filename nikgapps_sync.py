from NikGapps.Helper import Constants, Args
from NikGapps.OEM.Operations import Operations

start_time = Constants.start_of_function()

args = Args()
android_versions = args.get_android_versions()

for android_version in android_versions:
    Operations.sync_with_nikgapps_tracker(android_version)

Constants.end_of_function(start_time, "End of the program")
