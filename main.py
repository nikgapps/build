#!/usr/bin/env python
import sys
from NikGapps.Helper import FileOp
from Release import Release
import Config
from NikGapps.Helper.Constants import Constants
from NikGapps.Helper.Git import Git
import pytz
from datetime import datetime
import platform
import psutil
print("Start of the Program")
start_time = Constants.start_of_function()
mem = psutil.virtual_memory()
total_ram_in_bytes = mem.total
total_ram_in_gb = round(mem.total / 1073741824, 2)
print("---------------------------------------")
print("Ram: " + str(total_ram_in_bytes) + " bytes, " + str(total_ram_in_gb) + " Gb")
print("---------------------------------------")
local = datetime.now()
print("Local:", local.strftime("%a, %m/%d/%Y, %H:%M:%S"))

tz_NY = pytz.timezone('America/New_York')
datetime_NY = datetime.now(tz_NY)
print("NY:", datetime_NY.strftime("%a, %m/%d/%Y, %H:%M:%S"))

tz_London = pytz.timezone('Europe/London')
datetime_London = datetime.now(tz_London)
print("London:", datetime_London.strftime("%a, %m/%d/%Y, %H:%M:%S"))
print("---------------------------------------")
print("Running on system: " + platform.system())
print("---------------------------------------")

commit_message = datetime_London.strftime("%Y-%m-%d %H:%M:%S")
# find the argument length
arg_len = len(sys.argv)
# initialize android versions and package list to build
android_versions = [Config.TARGET_ANDROID_VERSION]
package_list = Config.BUILD_PACKAGE_LIST
if arg_len > 1:
    android_versions = sys.argv[1].split(',')
    if arg_len > 2:
        package_list = sys.argv[2].split(',')

print("Android Versions to build: " + str(android_versions))
print("Packages to build: " + str(package_list))

# # override when we don't want to execute anything
# android_versions = []

release_repo = None
source_last_commit_datetime = None
if Config.GIT_CHECK:
    if FileOp.dir_exists(Constants.release_history_directory):
        release_repo = Git(Constants.release_history_directory)
    else:
        print(Constants.release_history_directory + " doesn't exist!")
    source_repo = Git(Constants.cwd)
    source_last_commit_datetime = source_repo.get_latest_commit_date(repo="main")
    print("Last Source Commit: " + str(source_last_commit_datetime))

for android_version in android_versions:
    Config.TARGET_ANDROID_VERSION = int(android_version)
    apk_source_datetime = None
    release_datetime = None
    new_release = False
    if Config.GIT_CHECK:
        if release_repo is not None:
            release_datetime = release_repo.get_latest_commit_date(filter_key=str(Config.TARGET_ANDROID_VERSION))
            print("Last Release: " + str(release_datetime))
        if FileOp.dir_exists(Constants.apk_source_directly):
            apk_source_repo = Git(Constants.apk_source_directly + str(Config.TARGET_ANDROID_VERSION))
            if apk_source_repo is not None:
                apk_source_datetime = apk_source_repo.get_latest_commit_date()
                # if last commit was before release date, the release was already made so we don't need a new release
                print("Last Apk Repo (" + str(Config.TARGET_ANDROID_VERSION) + ") Commit: " + str(apk_source_datetime))
        else:
            print(Constants.apk_source_directly + " doesn't exist!")
        if apk_source_datetime is None or source_last_commit_datetime is None or release_datetime is None:
            new_release = True
        if new_release or apk_source_datetime > release_datetime or source_last_commit_datetime > release_datetime:
            new_release = True
    else:
        new_release = True
    if Config.OVERRIDE_RELEASE or new_release:
        if Config.TARGET_ANDROID_VERSION == 10 and "go" not in Config.BUILD_PACKAGE_LIST:
            Config.BUILD_PACKAGE_LIST.append("go")
        Constants.update_android_version_dependencies()
        today = datetime.now(pytz.timezone('Europe/London')).strftime("%a")
        if today != Config.RELEASE_DAY:
            Constants.update_sourceforge_release_directory("canary")
        else:
            Constants.update_sourceforge_release_directory("")
        Release.zip(package_list)
        if release_repo is not None:
            release_repo.git_push(str(android_version) + ": " + str(commit_message))

if Config.BUILD_CONFIG:
    if FileOp.dir_exists(Constants.config_directory):
        Constants.update_sourceforge_release_directory("config")
        zip_status = Release.zip(['config'])
    else:
        print(Constants.config_directory + " doesn't exist!")

website_repo = None
if FileOp.dir_exists(Constants.website_directory):
    if Config.GIT_CHECK:
        print("Updating the changelog to the website")
        website_repo = Git(Constants.website_directory)
        if website_repo is not None:
            commit_datetime = website_repo.get_latest_commit_date()
            website_repo.update_changelog()
Constants.end_of_function(start_time, "Total time taken by the program")
print("End of the Program")
