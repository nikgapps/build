import json

from NikGapps.Helper import FileOp, Constants
from NikGapps.OEM.PixelExperience import PixelExperience
from NikGapps.Git.Operations import Operations as GitOperations


class Operations:

    @staticmethod
    def get_pixel_experience_dict(android_version):
        pe = PixelExperience(android_version)
        pe.clone_gapps_image()
        return pe.get_gapps_dict()

    @staticmethod
    def get_pixel_experience_tracker(android_version, tracker_repo):
        repo_dir = tracker_repo.working_tree_dir
        if FileOp.dir_exists(repo_dir):
            print(f"{repo_dir} exists!")
            pixel_experience_tracker = repo_dir + Constants.dir_sep + f"pixel_experience_{android_version}.json"
            if FileOp.file_exists(pixel_experience_tracker):
                return pixel_experience_tracker, True
            else:
                print(f"{pixel_experience_tracker} does not exist!")
                return pixel_experience_tracker, False
        else:
            print(f"{repo_dir} doesn't exist!")
        return None, False

    @staticmethod
    def sync_with_pixel_experience_tracker(android_version):
        pixel_experience_dict = Operations.get_pixel_experience_dict(android_version)
        tracker_repo = GitOperations.setup_tracker_repo()
        pixel_experience_tracker = Operations.get_pixel_experience_tracker(android_version, tracker_repo)
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
