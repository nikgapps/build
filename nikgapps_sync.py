from NikGapps.Helper import C, Args
from NikGapps.OEM.Operations import Operations

start_time = C.start_of_function()

args = Args()
android_versions = args.get_android_versions()
list_of_supported_appsets = ["GoogleDialer"]
for android_version in android_versions:
    # Operations.sync_with_nikgapps_tracker(android_version)
    Operations.update_nikgapps_controller(android_version, list_of_supported_appsets)

C.end_of_function(start_time, "End of the program")
