from helper.NikGappsConfig import NikGappsConfig
from helper.git.GitOperations import GitOperations
from helper.Statics import Statics
from helper.web.TelegramApi import TelegramApi
from helper.web.Upload import Upload
from Release import Release
from helper.Config import FETCH_PACKAGE
from helper import Config
from colorama import Fore
from ondemand.ConfigOperations import ConfigOperations


class Operation:

    @staticmethod
    def fetch(android_versions):
        for android_version in android_versions:
            pkg_list = Release.package(FETCH_PACKAGE, android_version)
            if pkg_list.__len__() > 0:
                message = "Packages Successfully Fetched"
                print(message)
            else:
                message = "Fetching Failed"
                print(message)

    @staticmethod
    def is_new_release(source_last_commit_datetime, apk_source_datetime, release_datetime):
        if apk_source_datetime is None or release_datetime is None or source_last_commit_datetime is None:
            print(f"There never really was a release done for android {str(Config.TARGET_ANDROID_VERSION)}")
            return True

        source_last_commit_datetime_ago = release_datetime - source_last_commit_datetime
        if str(source_last_commit_datetime_ago).startswith("-"):
            print("Last Release was " + str(
                source_last_commit_datetime_ago * -1) + " before source update." + Fore.GREEN + " Eligible for new release!" + Fore.RESET)
        else:
            print("Last source update was " + str(
                source_last_commit_datetime_ago) + " before release." + Fore.YELLOW + " latest updates are already in the release!" + Fore.RESET)

        apk_source_datetime_ago = release_datetime - apk_source_datetime
        if str(apk_source_datetime_ago).startswith("-"):
            print("Last Release was " + str(
                apk_source_datetime_ago * -1) + " before apk update." + Fore.GREEN + " Eligible for new release!" + Fore.RESET)
        else:
            print("Last Apk update was " + str(
                apk_source_datetime_ago) + " before release." + Fore.YELLOW + " latest updates are already in the release!" + Fore.RESET)

        # check if apk source or source code is newer than last release
        if apk_source_datetime > release_datetime or source_last_commit_datetime > release_datetime:
            return True
        # if nothing is true yet, it's already a new release
        return False

    def build(self, android_versions, telegram: TelegramApi, git_check=Config.GIT_CHECK,
              package_list=Config.BUILD_PACKAGE_LIST,
              commit_message=None, sign_zip=Config.SIGN_ZIP, send_zip_device=Config.SEND_ZIP_DEVICE,
              fresh_build=Config.FRESH_BUILD):
        release_repo = None
        source_last_commit_datetime = None
        if git_check:
            source_last_commit_datetime = GitOperations.get_last_commit_date(
                branch="main" if Config.RELEASE_TYPE.__eq__("stable") else "dev")
            print(f"Last {str(Config.RELEASE_TYPE).capitalize()} Source Commit: " + str(source_last_commit_datetime))
            release_repo = GitOperations.get_release_repo(Config.RELEASE_TYPE)
        else:
            print("Git Check is disabled")
        for android_version in android_versions:
            upload = Upload(android_version=android_version, upload_files=Config.UPLOAD_FILES,
                            release_type=Config.RELEASE_TYPE)
            Config.TARGET_ANDROID_VERSION = android_version
            new_release = True
            # clone the apk repo if it doesn't exist
            if git_check:
                release_datetime = None
                if release_repo is not None:
                    release_datetime = release_repo.get_latest_commit_date(branch="master",
                                                                           filter_key=str(android_version))
                    print(f"Last Release ({str(android_version)}): " + str(release_datetime))
                apk_source_datetime = GitOperations.get_last_commit_date(android_version=str(android_version),
                                                                         branch="main" if Config.RELEASE_TYPE.__eq__(
                                                                             "stable") else "canary")
                if apk_source_datetime is not None:
                    print("Last Apk Repo (" + str(Config.TARGET_ANDROID_VERSION) + ") Commit: " + str(
                        apk_source_datetime))
                else:
                    print(Statics.pwd + Statics.dir_sep + str(android_version) + " doesn't exist!")
                new_release = self.is_new_release(source_last_commit_datetime, apk_source_datetime, release_datetime)
            if Config.OVERRIDE_RELEASE or new_release:
                Release.zip(package_list, android_version, sign_zip, send_zip_device, fresh_build, telegram, upload)
                if release_repo is not None and git_check:
                    release_repo.git_push(str(android_version) + ": " + str(commit_message))
            if Config.UPLOAD_FILES:
                config = NikGappsConfig(android_version=android_version)
                ConfigOperations.upload_nikgapps_config(config, android_version, upload)
            upload.close_connection()

        if git_check:
            website_repo = GitOperations.get_website_repo_for_changelog()
            if website_repo is not None:
                website_repo.update_changelog()
