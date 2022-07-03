#!/usr/bin/env python
import getopt
import sys
from NikGapps.Helper import FileOp, NikGappsConfig, B64
from Release import Release
import Config
from NikGapps.Helper.Constants import Constants
from NikGapps.Helper.Git import Git
from NikGapps.Helper.SystemStat import SystemStat
import pytz
from datetime import datetime
from Config import FETCH_PACKAGE
from Config import PROJECT_MODE

print("Start of the Program")

SystemStat.show_stats()

start_time = Constants.start_of_function()

tz_London = pytz.timezone('Europe/London')
datetime_London = datetime.now(tz_London)
print("London:", datetime_London.strftime("%a, %m/%d/%Y, %H:%M:%S"))
print("---------------------------------------")
commit_message = datetime_London.strftime("%Y-%m-%d %H:%M:%S")
# initialize android versions and package list to build
android_versions = [Config.TARGET_ANDROID_VERSION]
package_list = Config.BUILD_PACKAGE_LIST

argumentList = sys.argv[1:]
print(f"Actual Arguments: {argumentList}")
# Options
options = "ucnpad:"
# Long options
long_options = ["userID=", "config=", "name=", "androidversion=", "packages=", "disableGitCheck="]
try:
    config_string = None
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)
    print(f"Arguments with values: {arguments}")
    # checking each argument
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-u", "--userID"):
            user_id = currentValue
        if currentArgument in ("-c", "--config"):
            config_string = B64.b64d(currentValue)
            if config_string != currentValue:
                print(config_string)
                package_list = []
            else:
                print("Cannot decode the input file")
                exit(1)
        if config_string is None and currentArgument in ("-p", "--packages"):
            package_list = currentValue.split(',')
        if currentArgument in ("-n", "--name"):
            file_name = f"{currentValue}" if currentValue.endswith(".config") else f"{currentValue}.config"
        if currentArgument in ("-a", "--androidversion"):
            android_versions = currentValue.split(',')
        if currentArgument in ("-d", "--disableGitCheck"):
            Config.GIT_CHECK = False
    if config_string is not None:
        # fetch the config repository
        # create a file by reading config_string
        # build and upload the package
        # move the file to archive
        print("config operation")
    else:
        print("package operation")

except getopt.error as err:
    # output error, and return with an error code
    print(str(err))
    exit(0)

print("---------------------------------------")
print("Android Versions to build: " + str(android_versions))
print("---------------------------------------")
print("Packages to build: " + str(package_list))
print("---------------------------------------")

# # override when we don't want to execute anything
# android_versions = []

if PROJECT_MODE.__eq__("fetch"):
    pkg_list = Release.package(FETCH_PACKAGE)
    if pkg_list.__len__() > 0:
        message = "Packages Successfully Fetched"
        print(message)
    else:
        message = "Fetching Failed"
        print(message)
else:
    release_repo = None
    source_last_commit_datetime = None
    if Config.GIT_CHECK:
        if FileOp.dir_exists(Constants.release_history_directory):
            release_repo = Git(Constants.release_history_directory)
        else:
            print(Constants.release_history_directory + " doesn't exist!")
        source_repo = Git(Constants.cwd)
        source_last_commit_datetime = source_repo.get_latest_commit_date(repo="main")
        if Config.RELEASE_TYPE.__eq__("canary"):
            print("Last Canary Source Commit: " + str(source_last_commit_datetime))
        else:
            print("Last Source Commit: " + str(source_last_commit_datetime))

    for android_version in android_versions:
        Config.TARGET_ANDROID_VERSION = android_version
        apk_source_datetime = None
        release_datetime = None
        new_release = False
        if Config.GIT_CHECK:
            if release_repo is not None:
                release_datetime = release_repo.get_latest_commit_date(filter_key=str(Config.TARGET_ANDROID_VERSION))
                print("Last Release: " + str(release_datetime))
            if FileOp.dir_exists(Constants.apk_source_directly):
                branch = "master"
                if Config.RELEASE_TYPE.__eq__("canary"):
                    branch = "canary"
                apk_source_repo = Git(Constants.apk_source_directly + str(Config.TARGET_ANDROID_VERSION))
                if apk_source_repo is not None:
                    apk_source_datetime = apk_source_repo.get_latest_commit_date(repo=branch)
                    # if last commit was before release date,
                    # the release was already made, so we don't need a new release
                    print("Last Apk Repo (" + str(Config.TARGET_ANDROID_VERSION) + ") Commit: " + str(
                        apk_source_datetime))
            else:
                print(Constants.apk_source_directly + " doesn't exist!")
            if apk_source_datetime is None or source_last_commit_datetime is None or release_datetime is None:
                new_release = True
            if new_release or apk_source_datetime > release_datetime or source_last_commit_datetime > release_datetime:
                new_release = True
            if release_datetime is not None:
                apk_source_datetime_ago = release_datetime - apk_source_datetime
                if str(apk_source_datetime_ago).startswith("-"):
                    print("Last Release was " + str(apk_source_datetime_ago * -1) + " before apk update")
                else:
                    print("Last Apk update was " + str(apk_source_datetime_ago) + " before release")
                source_last_commit_datetime_ago = release_datetime - source_last_commit_datetime
                if str(source_last_commit_datetime_ago).startswith("-"):
                    print("Last Release was " + str(source_last_commit_datetime_ago * -1) + " before source update")
                else:
                    print("Last source update was " + str(source_last_commit_datetime_ago) + " before release")
            else:
                print(f"There never really was a release done for android {str(Config.TARGET_ANDROID_VERSION)}")
        else:
            new_release = True
        if Config.OVERRIDE_RELEASE or new_release:
            if Config.TARGET_ANDROID_VERSION == 10 and "go" not in Config.BUILD_PACKAGE_LIST:
                Config.BUILD_PACKAGE_LIST.append("go")
            Constants.update_android_version_dependencies()
            today = datetime.now(pytz.timezone('Europe/London')).strftime("%a")
            if Config.RELEASE_TYPE.__eq__("canary"):
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
        website_repo = Git(Constants.website_directory)
        if website_repo is not None:
            commit_datetime = website_repo.get_latest_commit_date()
            website_repo.update_changelog()

config = NikGappsConfig()
config.upload_nikgapps_config()

Constants.end_of_function(start_time, "Total time taken by the program")
print("End of the Program")
