from datetime import datetime

from NikGapps.Config.ConfigOperations import ConfigOperations
from NikGapps.Config.NikGappsConfig import NikGappsConfig
from NikGapps.Helper import FileOp, Git, Upload
from NikGapps.Helper.Constants import Constants
from Release import Release
from Config import FETCH_PACKAGE
import Config
import pytz
from colorama import Fore


class Operation:

    @staticmethod
    def fetch():
        pkg_list = Release.package(FETCH_PACKAGE)
        if pkg_list.__len__() > 0:
            message = "Packages Successfully Fetched"
            print(message)
        else:
            message = "Fetching Failed"
            print(message)

    @staticmethod
    def get_last_commit_date(repo_dir=Constants.cwd, repo_url=None,
                             branch="canary" if Config.RELEASE_TYPE.__eq__("canary") else "main"):
        last_commit_datetime = None
        repository = Git(repo_dir)
        if repo_url is not None:
            repository.clone_repo(repo_url=repo_url, fresh_clone=False, branch=branch)
        if repository is not None:
            last_commit_datetime = repository.get_latest_commit_date(branch=branch)
        return last_commit_datetime

    @staticmethod
    def get_release_repo():
        release_repo = Git(Constants.release_history_directory)
        if not FileOp.dir_exists(Constants.release_history_directory):
            repo_name = "git@github.com:nikgapps/canary-release.git" if Config.RELEASE_TYPE.__eq__(
                "canary") else "git@github.com:nikgapps/release.git"
            release_repo.clone_repo(repo_name, branch="master", commit_depth=50)
            if not FileOp.dir_exists(Constants.release_history_directory):
                print(Constants.release_history_directory + " doesn't exist!")
        return release_repo

    @staticmethod
    def get_website_repo_for_changelog(repo_dir=Constants.website_directory, repo_url=Constants.website_repo,
                                       branch="master"):
        repo = Git(repo_dir)
        if repo_url is not None:
            repo.clone_repo(repo_url=repo_url, fresh_clone=False, branch=branch)
        if not FileOp.dir_exists(Constants.website_directory):
            print(f"Repo {repo_dir} doesn't exist!")
        return repo

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

    def build(self, git_check=Config.GIT_CHECK, android_versions=None, package_list=Config.BUILD_PACKAGE_LIST,
              commit_message=None, upload: Upload = None):
        if android_versions is None:
            android_versions = [Config.TARGET_ANDROID_VERSION]
        if commit_message is None:
            commit_message = datetime.now(pytz.timezone('Europe/London')).strftime("%Y-%m-%d %H:%M:%S")
        release_repo = None
        website_repo = None
        source_last_commit_datetime = None
        if git_check:
            source_last_commit_datetime = self.get_last_commit_date(branch="main")
            print(f"Last {str(Config.RELEASE_TYPE).capitalize()} Source Commit: " + str(source_last_commit_datetime))
            release_repo = self.get_release_repo()
            website_repo = self.get_website_repo_for_changelog()
        else:
            print("Git Check is disabled")
        for android_version in android_versions:
            Config.TARGET_ANDROID_VERSION = android_version
            # clone the apk repo if it doesn't exist
            apk_source_directory = Constants.apk_source_directory + str(android_version)
            apk_source_repo = Constants.apk_source_repo + str(android_version) + ".git"
            if git_check:
                release_datetime = None
                if release_repo is not None:
                    release_datetime = release_repo.get_latest_commit_date(branch="master",
                                                                           filter_key=str(android_version))
                    print(f"Last Release ({str(android_version)}): " + str(release_datetime))
                apk_source_datetime = self.get_last_commit_date(repo_dir=apk_source_directory,
                                                                repo_url=apk_source_repo)
                if apk_source_datetime is not None:
                    print("Last Apk Repo (" + str(Config.TARGET_ANDROID_VERSION) + ") Commit: " + str(
                        apk_source_datetime))
                else:
                    print(Constants.apk_source_directory + " doesn't exist!")
                new_release = self.is_new_release(source_last_commit_datetime, apk_source_datetime, release_datetime)
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
                Release.zip(package_list, upload)
                if release_repo is not None and git_check:
                    release_repo.git_push(str(android_version) + ": " + str(commit_message))

        if git_check and website_repo is not None:
            website_repo.update_changelog()

        if Config.UPLOAD_FILES:
            config = NikGappsConfig()
            ConfigOperations.upload_nikgapps_config(config)
