import json

from NikGapps.Helper import FileOp, C
from NikGapps.Helper.Json import Json
from NikGapps.OEM.ApkMirror import ApkMirror
from NikGapps.OEM.EvoX import EvoX
from NikGapps.OEM.NikGapps import NikGapps
from NikGapps.OEM.PixelExperience import PixelExperience
from NikGapps.Git.Operations import Operations as GitOperations
from NikGappsPackages import NikGappsPackages


class Operations:
    @staticmethod
    def get_tracker(android_version, tracker_repo, oem):
        repo_dir = tracker_repo.working_tree_dir
        if FileOp.dir_exists(repo_dir):
            print(f"{repo_dir} exists!")
            tracker_file = repo_dir + C.dir_sep + android_version + C.dir_sep + f"{oem}_{android_version}.json"
            if FileOp.file_exists(tracker_file):
                return tracker_file, True
            else:
                print(f"{tracker_file} does not exist!")
                return tracker_file, False
        else:
            print(f"{repo_dir} doesn't exist!")
        return None, False

    @staticmethod
    def sync_with_nikgapps_tracker(android_version):
        tracker_repo = GitOperations.setup_tracker_repo()
        if tracker_repo is None:
            print("Failed to setup tracker repo!")
            return
        n = NikGapps(android_version)
        tracker_file, isexists = Operations.get_tracker(android_version, tracker_repo, n.tracker_key)
        if tracker_file is not None:
            n_gapps_dict = n.get_nikgapps_dict(NikGappsPackages.get_packages("all"))
            if n_gapps_dict is not None:
                Json.write_dict_to_file(n_gapps_dict, tracker_file)
                if isexists:
                    print(f"Updated {tracker_file}")
                    tracker_repo.update_repo_changes("Synced with NikGapps Tracker for " + android_version)
                else:
                    print("File is empty!")
                    tracker_repo.update_repo_changes(
                        "Initial commit for NikGapps tracker for android version: " + android_version)
            else:
                print("Failed to get NikGapps GApps Dict!")
        else:
            print("NikGapps Tracker is None!")

    @staticmethod
    def update_nikgapps_controller(android_version, list_of_appsets=None):
        tracker_repo = GitOperations.setup_tracker_repo()
        if tracker_repo is None:
            print("Failed to setup tracker repo!")
            return
        n = NikGapps(android_version)
        tracker_file, isexists = Operations.get_tracker(android_version, tracker_repo, n.version_key)
        appset_list = []
        if list_of_appsets is not None:
            for appset in list_of_appsets:
                for app in NikGappsPackages.get_packages(appset):
                    appset_list.append(app)
        else:
            appset_list = NikGappsPackages.get_packages("all")
        n_gapps_dict = n.get_nikgapps_controller(appset_list=appset_list,
                                                 nikgapps_dict=Json.read_dict_from_file(tracker_file))
        if tracker_file is not None:
            if n_gapps_dict is not None:
                Json.write_dict_to_file(n_gapps_dict, tracker_file)
                if isexists:
                    print(f"Updating {tracker_file}")
                    tracker_repo.update_repo_changes("Synced with NikGapps Tracker for " + android_version)
                else:
                    print("File is empty!")
                    tracker_repo.update_repo_changes(
                        "Initial commit for NikGapps tracker for android version: " + android_version)
            else:
                print("NikGapps Tracker is None!")
        else:
            print("NikGapps Tracker is None!")

    @staticmethod
    def sync_with_evo_x_tracker(android_version):
        tracker_repo = GitOperations.setup_tracker_repo()
        if tracker_repo is None:
            print("Failed to setup tracker repo!")
            return
        evo = EvoX(android_version)
        tracker_file, isexists = Operations.get_tracker(android_version, tracker_repo, evo.oem)
        if tracker_file is not None:
            evo_gapps_dict = evo.get_evo_x_dict()
            if evo_gapps_dict is not None:
                Json.write_dict_to_file(evo_gapps_dict, tracker_file)
                if isexists:
                    print(f"Updated {tracker_file}")
                    tracker_repo.update_repo_changes("Synced with Evo X Tracker for " + android_version)
                else:
                    print("File is empty!")
                    tracker_repo.update_repo_changes(
                        "Initial commit for Evo X tracker for android version: " + android_version)
            else:
                print("Evo X Tracker is None!")
        else:
            print("Evo X Tracker is None!")

    @staticmethod
    def sync_with_pixel_experience_tracker(android_version):
        tracker_repo = GitOperations.setup_tracker_repo()
        if tracker_repo is None:
            print("Failed to setup tracker repo!")
            return
        pe = PixelExperience(android_version)
        pixel_experience_tracker = Operations.get_tracker(android_version, tracker_repo, pe.oem)
        if pixel_experience_tracker[0] is not None:
            pixel_experience_dict = pe.get_pixel_experience_dict()
            if pixel_experience_dict is not None:
                Json.write_dict_to_file(pixel_experience_dict, pixel_experience_tracker[0])
                if pixel_experience_tracker[1]:
                    print(f"Updated {pixel_experience_tracker[0]}")
                    tracker_repo.update_repo_changes("Synced with PixelExperience Tracker")
                else:
                    print("File is empty!")
                    tracker_repo.update_repo_changes("Initial commit for Pixel Experience tracker")
            else:
                print("Pixel Experience Tracker is None!")
        else:
            print("Pixel Experience Tracker is None!")

    @staticmethod
    def sync_with_apk_mirror(android_version):
        tracker_repo = GitOperations.setup_tracker_repo()
        if tracker_repo is None:
            print("Failed to setup tracker repo!")
            return
        am = ApkMirror(android_version)
        apk_mirror_tracker, isexists = Operations.get_tracker(android_version, tracker_repo, am.oem)
        if apk_mirror_tracker is not None:
            am_dict = am.get_apk_mirror_dict(NikGappsPackages.get_packages("all"))
            if am_dict is not None:
                Json.write_dict_to_file(am_dict, apk_mirror_tracker)
                if isexists:
                    print(f"Updated {apk_mirror_tracker}")
                    tracker_repo.update_repo_changes("Synced with Apk Mirror Tracker for " + android_version)
                else:
                    print("File is empty!")
                    tracker_repo.update_repo_changes(
                        "Initial commit for Apk Mirror tracker for android version: " + android_version)
            else:
                print("Failed to get Apk Mirror Dict!")
        else:
            print("Apk Mirror Tracker is None!")
