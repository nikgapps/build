import json

from NikGapps.Helper import FileOp, Constants
from NikGapps.OEM.NikGapps import NikGapps
from NikGapps.OEM.PixelExperience import PixelExperience
from NikGapps.Git.Operations import Operations as GitOperations


class Operations:
    @staticmethod
    def get_tracker(android_version, tracker_repo, oem):
        repo_dir = tracker_repo.working_tree_dir
        if FileOp.dir_exists(repo_dir):
            print(f"{repo_dir} exists!")
            tracker_file = repo_dir + Constants.dir_sep + f"{oem}_{android_version}.json"
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
        n = NikGapps(android_version)
        n_gapps_dict = n.get_nikgapps_dict()
        tracker_repo = GitOperations.setup_tracker_repo()
        if tracker_repo is None:
            print("Failed to setup tracker repo!")
            return
        tracker = Operations.get_tracker(android_version, tracker_repo, n.tracker)
        if tracker[0] is not None:
            with open(tracker[0], 'w') as file:
                json_dumps_str = json.dumps(n_gapps_dict, indent=4, sort_keys=True)
                print(json_dumps_str, file=file)
            if tracker[1]:
                print(f"Updated {tracker[0]}")
                tracker_repo.update_repo_changes("Synced with NikGapps Tracker for " + android_version)
            else:
                print("File is empty!")
                tracker_repo.update_repo_changes(
                    "Initial commit for NikGapps tracker for android version: " + android_version)
        else:
            print("NikGapps Tracker is None!")

    @staticmethod
    def sync_with_pixel_experience_tracker(android_version):
        pe = PixelExperience(android_version)
        pixel_experience_dict = pe.get_pixel_experience_dict()
        tracker_repo = GitOperations.setup_tracker_repo()
        if tracker_repo is None:
            print("Failed to setup tracker repo!")
            return
        pixel_experience_tracker = Operations.get_tracker(android_version, tracker_repo, pe.tracker)
        if pixel_experience_tracker[0] is not None:
            with open(pixel_experience_tracker[0], 'w') as file:
                json_dumps_str = json.dumps(pixel_experience_dict, indent=4, sort_keys=True)
                print(json_dumps_str, file=file)
            if pixel_experience_tracker[1]:
                print(f"Updated {pixel_experience_tracker[0]}")
                tracker_repo.update_repo_changes("Synced with PixelExperience Tracker")
            else:
                print("File is empty!")
                tracker_repo.update_repo_changes("Initial commit for Pixel Experience tracker")
        else:
            print("Pixel Experience Tracker is None!")
