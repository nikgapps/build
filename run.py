#!/usr/bin/env python

from helper.Args import Args
from Operation import Operation
from helper import Config
from helper.SystemStat import SystemStat
from helper.Config import PROJECT_MODE
from helper.P import P
from helper.T import T
from helper.web.TelegramApi import TelegramApi

print("Start of the Program")
SystemStat.show_stats()

t = T()
P.green("---------------------------------------")
commit_message = t.get_london_date_time("%Y-%m-%d %H:%M:%S")

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

operation = Operation()
telegram = TelegramApi(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID)
if PROJECT_MODE.__eq__("fetch"):
    operation.fetch(android_versions)
else:
    operation.build(git_check=args.enable_git_check, android_versions=android_versions,
                    package_list=package_list, commit_message=commit_message, telegram=telegram)

t.taken("Total time taken by the program")

print("End of the Program")
