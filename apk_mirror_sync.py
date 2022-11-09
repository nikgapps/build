
from NikGapps.Helper import Args
from NikGapps.OEM.Operations import Operations

args = Args()
android_versions = args.get_android_versions()
for android_version in android_versions:
    Operations.sync_with_apk_mirror(android_version)
