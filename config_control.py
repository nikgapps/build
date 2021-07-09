import sys
import Config
from Release import Release
from NikGapps.Helper.Constants import Constants
from NikGapps.Helper.FileOp import FileOp

start_time = Constants.start_of_function()

if Config.BUILD_CONFIG:
    arg_len = len(sys.argv)
    android_versions = [Config.TARGET_ANDROID_VERSION]
    if arg_len > 1:
        android_versions = sys.argv[1].split(',')
    print("---------------------------------------")
    print("Android Versions to build: " + str(android_versions))
    print("---------------------------------------")
    if FileOp.dir_exists(Constants.config_directory):
        for android_version in android_versions:
            Config.TARGET_ANDROID_VERSION = int(android_version)
            Constants.update_android_version_dependencies()
            Constants.update_sourceforge_release_directory("config")
            zip_status = Release.zip(['config'])
    else:
        print(Constants.config_directory + " doesn't exist!")

Constants.end_of_function(start_time, "Total time taken by the program to build custom builds")
