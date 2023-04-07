#!/usr/bin/env python

from colorama import Fore

from NikGapps.Helper import FileOp
from NikGapps.Helper.Args import Args
from NikGapps.Web.Upload import Upload
from Operation import Operation
import Config
from NikGapps.Helper.C import C
from NikGapps.Helper.SystemStat import SystemStat
import pytz
from datetime import datetime
from Config import PROJECT_MODE
from Release import Release

print("Start of the Program")
print(Fore.GREEN)
SystemStat.show_stats()
start_time = C.start_of_function()
tz_London = pytz.timezone('Europe/London')
datetime_London = datetime.now(tz_London)
print("London:", datetime_London.strftime("%a, %m/%d/%Y, %H:%M:%S"))
print("---------------------------------------")
commit_message = datetime_London.strftime("%Y-%m-%d %H:%M:%S")
print(Fore.RESET)
# initialize android versions and package list to build
android_versions = [Config.TARGET_ANDROID_VERSION]
package_list = Config.BUILD_PACKAGE_LIST

# parse command line arguments
args = Args()
Config.OVERRIDE_RELEASE = args.forceRun
if len(args.get_package_list()) > 0:
    package_list = args.get_package_list()
# override when we don't want to execute anything
# android_versions = []

if len(args.get_android_versions()) > 0:
    android_versions = args.get_android_versions()
print("---------------------------------------")
print("Android Versions to build: " + str(android_versions))
print("---------------------------------------")
print("Packages to build: " + str(package_list))
print("---------------------------------------")

if PROJECT_MODE.__eq__("fetch"):
    operation = Operation()
    operation.fetch()
else:
    operation = Operation()
    if Config.RELEASE_TYPE.__eq__("canary"):
        C.update_sourceforge_release_directory("canary")
    u = Upload()
    operation.build(git_check=args.enable_git_check, android_versions=android_versions,
                    package_list=package_list, commit_message=commit_message, upload=u)
    u.close_connection()

C.end_of_function(start_time, "Total time taken by the program")

print("End of the Program")
