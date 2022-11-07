from datetime import datetime

import pytz
from colorama import Fore

import Config
from NikGapps.Config.UserBuild.OnDemand import OnDemand
from NikGapps.Helper import SystemStat, C, Args, B64, FileOp
from Operation import Operation

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

# parse command line arguments
args = Args()
android_versions = args.get_android_versions()

if len(android_versions) == 0:
    print("No Android version specified. Exiting...")
    exit(1)

if len(android_versions) > 1:
    print("Only one android version can be specified. Exiting...")
    exit(1)

Config.TARGET_ANDROID_VERSION = android_versions[0]

config_name = args.config_name
if config_name is None:
    print("No config name specified. Exiting...")
    exit(1)

config_string = args.config_value
if config_string is None:
    print("No config value specified. Exiting...")
    exit(1)

# now that we have the validations done, let's check the directories
repo_dir = C.pwd + C.dir_sep + str(Config.TARGET_ANDROID_VERSION)
if FileOp.dir_exists(repo_dir):
    print(f"{repo_dir} already exists!")
else:
    print(f"{repo_dir} does not exist. Cloning...")
    if Operation.clone_apk_repo(android_version=Config.TARGET_ANDROID_VERSION) is not None:
        print(f"{repo_dir} cloned successfully!")
    else:
        print(f"{repo_dir} could not be cloned!")
        exit(1)

if not OnDemand.build_from_config_byte(config_name, config_string, Config.TARGET_ANDROID_VERSION):
    print("Failed to build. Exiting...")
else:
    print("Build successful!")

print("End of the Program")
