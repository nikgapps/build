from NikGapps.Helper import C, Args
from NikGapps.OEM.Operations import Operations

start_time = C.start_of_function()

args = Args()
android_versions = args.get_android_versions()

for android_version in android_versions:
    Operations.sync_with_evo_x_tracker(android_version)

C.end_of_function(start_time, "End of the program")
