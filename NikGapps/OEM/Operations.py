import json

from NikGapps.Helper import FileOp, C, Package
from NikGapps.Helper.Json import Json
from NikGapps.OEM.ApkMirror import ApkMirror
from NikGapps.OEM.Cheetah import Cheetah
from NikGapps.OEM.EvoX import EvoX
from NikGapps.OEM.NikGapps import NikGapps
from NikGapps.OEM.PixelExperience import PixelExperience
from NikGapps.Git.Operations import Operations as GitOperations
from NikGappsPackages import NikGappsPackages


class Operations:

    @staticmethod
    def sync_tracker(oem, android_version, tracker_repo=None, appsets=None):
        oem = oem.lower()
        if oem == "pixelexperience":
            return Operations.sync_with_pixel_experience_tracker(android_version, tracker_repo, appsets)
        elif oem == "evox":
            return Operations.sync_with_evo_x_tracker(android_version, tracker_repo, appsets)
        elif oem == "apk_mirror":
            return Operations.sync_with_apk_mirror(android_version, tracker_repo, appsets)
        elif oem == "nikgapps":
            return Operations.sync_with_nikgapps_tracker(android_version, tracker_repo)
        elif oem == "cheetah":
            return Operations.sync_with_cheetah_tracker(android_version, tracker_repo, appsets)
        else:
            raise Exception(f"Unknown OEM: {oem}")

    @staticmethod
    def get_tracker_dict(oem, android_version, tracker_repo, appsets=None):
        oem = oem.lower()
        if oem == "pixelexperience":
            return Operations.sync_with_pixel_experience_tracker(android_version, tracker_repo, appsets,
                                                                 return_dict=True)
        elif oem == "evox":
            return Operations.sync_with_evo_x_tracker(android_version, tracker_repo, appsets, return_dict=True)
        elif oem == "apk_mirror":
            return Operations.sync_with_apk_mirror(android_version, tracker_repo, appsets, return_dict=True)
        elif oem == "nikgapps":
            return Operations.sync_with_nikgapps_tracker(android_version, tracker_repo, return_dict=True)
        elif oem == "cheetah":
            return Operations.sync_with_cheetah_tracker(android_version, tracker_repo, appsets, return_dict=True)
        else:
            raise Exception(f"Unknown OEM: {oem}")

    @staticmethod
    def get_tracker(android_version, repo_dir, oem):
        if FileOp.dir_exists(repo_dir):
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
    def get_oem_repo_dir(oem, android_version):
        oem = oem.lower()
        if oem == "pixelexperience":
            pe = PixelExperience(android_version)
            return pe.repo_dir
        elif oem == "evox":
            evox = EvoX(android_version)
            return evox.repo_dir
        elif oem == "apk_mirror":
            # this is TBD, we need to create a repo and then add the apks there
            return None
        elif oem == "nikgapps":
            ng = NikGapps(android_version)
            return ng.repo_dir
        elif oem == "cheetah":
            cheetah = Cheetah(android_version)
            return cheetah.repo_dir
        return None

    @staticmethod
    def get_nikgapps_appset(appset):
        appset_list = NikGappsPackages.get_packages(appset)
        if appset_list is not None:
            for app_set in appset_list:
                if str(app_set.title).lower() == appset.lower():
                    return app_set
        return None

    @staticmethod
    def get_nikgapps_package(appset, package):
        for pkg in appset.package_list:
            pkg: Package
            if pkg.package_name == package:
                return pkg
        return None

    @staticmethod
    def sync_with_nikgapps_tracker(android_version, tracker_repo, return_dict=False):
        n = NikGapps(android_version)
        tracker_file, isexists = Operations.get_tracker(android_version, tracker_repo.working_tree_dir, n.tracker_key)
        if tracker_file is not None:
            n_gapps_dict = n.get_nikgapps_dict(NikGappsPackages.get_packages("all"))
            if return_dict:
                return n_gapps_dict
            if n_gapps_dict is not None:
                Json.write_dict_to_file(n_gapps_dict, tracker_file)
                if isexists:
                    print(f"Updating {tracker_file}")
                    tracker_repo.update_repo_changes("Synced with NikGapps Tracker for " + android_version)
                else:
                    print("File is empty!")
                    tracker_repo.update_repo_changes(
                        "Initial commit for NikGapps tracker for android version: " + android_version)
                return tracker_file
            else:
                print("Failed to get NikGapps GApps Dict!")
                return None
        else:
            print("NikGapps Tracker is None!")
            return None

    @staticmethod
    def get_updater_dict(android_version, tracker_repo):
        if tracker_repo is None:
            tracker_repo = GitOperations.setup_tracker_repo()
            if tracker_repo is None:
                print("Failed to setup tracker repo!")
                return
        n = NikGapps(android_version)
        tracker_file, isexists = Operations.get_tracker(android_version, tracker_repo.working_tree_dir, n.update_key)
        return tracker_file, isexists

    @staticmethod
    def update_nikgapps_updater_dict(android_version, update_dict, tracker_repo=None):
        tracker_file, isexists = Operations.get_updater_dict(android_version, tracker_repo)
        Json.write_dict_to_file(update_dict, tracker_file)
        tracker_repo.update_repo_changes(f"The updater for {android_version} is updated")

    @staticmethod
    def get_oems_from_controller(android_version, tracker_repo=None, return_dict=False, return_file=False):
        if tracker_repo is None:
            tracker_repo = GitOperations.setup_tracker_repo()
            if tracker_repo is None:
                print("Failed to setup tracker repo!")
                return
        n = NikGapps(android_version)
        tracker_file, isexists = Operations.get_tracker(android_version, tracker_repo.working_tree_dir, n.version_key)
        if return_file:
            return tracker_file
        nikgapps_dict = Json.read_dict_from_file(tracker_file)
        if return_dict:
            return nikgapps_dict
        return Operations.get_oems_from_controller_dict(nikgapps_dict)

    @staticmethod
    def get_oems_from_controller_dict(nikgapps_dict):
        oems = []
        appsets = []
        if nikgapps_dict is not None:
            for appset in nikgapps_dict:
                appsets.append(appset)
                for pkg_dict in nikgapps_dict[appset]:
                    for pkg in pkg_dict:
                        for file_dict in pkg_dict[pkg]:
                            oem = file_dict["update_source"]
                            if oem not in oems:
                                oems.append(oem)
            return oems, appsets
        return None, None

    @staticmethod
    def get_appsets_from_controller_dict(nikgapps_dict, filter_oem=None):
        oems_appsets_dict = {}
        if nikgapps_dict is not None:
            for appset in nikgapps_dict:
                for pkg_dict in nikgapps_dict[appset]:
                    for pkg in pkg_dict:
                        for file_dict in pkg_dict[pkg]:
                            oem = file_dict["update_source"]
                            if filter_oem is None or filter_oem == oem:
                                oems_appsets_dict[appset] = oem
        return oems_appsets_dict

    @staticmethod
    def update_nikgapps_controller_version(controller_dict_file, appset_dict, oem_dict, oem):
        oem = oem.lower()
        controller_dict = Json.read_dict_from_file(controller_dict_file)
        if controller_dict is not None:
            for appset in controller_dict:
                if appset in appset_dict:
                    for pkg_dict in controller_dict[appset]:
                        for pkg in pkg_dict:
                            if pkg in oem_dict:
                                for file_dict in pkg_dict[pkg]:
                                    oem_pkg_dict = oem_dict[pkg]
                                    if oem_pkg_dict is not None:
                                        # file_name = str(Path(file_dict["file_path"]).name)
                                        oem_pkg_dict: dict
                                        # oem_length = len(oem_pkg_dict)
                                        for oem_file in oem_pkg_dict:
                                            file_name = oem_file["file"]
                                            if file_name.endswith(".apk.gz"):
                                                print(f"Updating {file_name} for {oem}")
                                                continue
                                            oem_pkg = oem_file["package"]
                                            if oem_pkg == pkg:
                                                # oem_file_name = str(Path(oem_file["file"]).name)
                                                file_dict[f"{oem}_version"] = oem_file["version"]
                                                file_dict[f"{oem}_version_code"] = oem_file["version_code"]
                                                file_dict[f"{oem}_v_code"] = oem_file["v_code"]
                                                file_dict[f"{oem}_size"] = oem_file["size"]
                                                file_dict[f"{oem}_location"] = oem_file["location"]
                            else:
                                print(f"Package {pkg} not found in {oem}!")
            Json.write_dict_to_file(controller_dict, controller_dict_file)
            return True
        return False

    @staticmethod
    def get_oem_file_list_dict(pkg, oem_dict):
        oem_file_list_dict = {}
        folder = None
        file_list = []
        # get the folder from the package as pkg is of primary apk, so that folder counts
        for oem_pkg in oem_dict:
            if str(pkg).__eq__(str(oem_pkg)) and folder is None:
                for oem_file in oem_dict[oem_pkg]:
                    folder = str(oem_file["folder"])
                    break
        if folder is not None:
            for oem_pkg in oem_dict:
                if str(oem_pkg).__eq__("branch"):
                    continue
                for oem_file in oem_dict[oem_pkg]:
                    file_pkg = oem_file["package"]
                    if str(folder).__eq__(str(oem_file["folder"])) or str(pkg).__eq__(file_pkg):
                        f_dict = {"partition": oem_file["partition"], "type": oem_file["type"],
                                  "folder": folder, "package": oem_file["package"],
                                  "file": oem_file["file"], "version_code": oem_file["version_code"],
                                  "version": oem_file["version"], "location": oem_file["location"]}
                        file_list.append(f_dict)
        if len(file_list) > 0:
            oem_file_list_dict[pkg] = file_list
        return oem_file_list_dict

    @staticmethod
    def get_nikgapps_controller_app_sets(list_of_appsets):
        appset_list = []
        if len(list_of_appsets) > 0:
            for appset in list_of_appsets:
                for app in NikGappsPackages.get_packages(appset):
                    if app is not None:
                        appset_list.append(app)
        else:
            appset_list = NikGappsPackages.get_packages("all")
        if len(appset_list) == 0:
            print("No appsets found!")
            return None
        return appset_list

    @staticmethod
    def get_changelog_controller(android_version, tracker_repo):
        n = NikGapps(android_version)
        tracker_file, isexists = Operations.get_tracker(android_version, tracker_repo.working_tree_dir, n.changelog_key)
        if isexists:
            return tracker_file
        else:
            # create an empty changelog file
            Json.write_dict_to_file({}, tracker_file)
            print("File is empty!")
            tracker_repo.update_repo_changes(
                "Initial commit for Changelog Controller for android version: " + android_version)
            return tracker_file

    @staticmethod
    def update_nikgapps_controller(android_version, tracker_repo, list_of_appsets):
        n = NikGapps(android_version)
        tracker_file, isexists = Operations.get_tracker(android_version, tracker_repo.working_tree_dir, n.version_key)
        controller_dict = {}
        if isexists:
            controller_dict = Json.read_dict_from_file(tracker_file)
            controller_oems, controller_appsets = Operations.get_oems_from_controller_dict(controller_dict)
            if len(controller_appsets) > 0 and len(list_of_appsets) > 0:
                for appset in controller_appsets:
                    if appset not in list_of_appsets:
                        list_of_appsets.append(appset)
        appset_list = Operations.get_nikgapps_controller_app_sets(list_of_appsets)
        n_gapps_dict = n.get_nikgapps_controller(appset_list=appset_list,
                                                 nikgapps_dict=controller_dict if isexists else None)
        if tracker_file is not None:
            if n_gapps_dict is not None:
                Json.write_dict_to_file(n_gapps_dict, tracker_file)
                if isexists:
                    print(f"Updating {tracker_file}")
                    tracker_repo.update_repo_changes("Synced with NikGapps Controller for " + android_version)
                else:
                    print("File is empty!")
                    tracker_repo.update_repo_changes(
                        "Initial commit for NikGapps Controller for android version: " + android_version)
                return tracker_file
            else:
                print("NikGapps Controller is None!")
                return None
        else:
            print("NikGapps Tracker is None!")
            return None

    @staticmethod
    def sync_with_cheetah_tracker(android_version, tracker_repo=None, appsets=None, return_dict=False):
        if tracker_repo is None:
            tracker_repo = GitOperations.setup_tracker_repo()
            if tracker_repo is None:
                print("Failed to setup tracker repo!")
                return None
        c = Cheetah(android_version)
        tracker_file, isexists = Operations.get_tracker(android_version, tracker_repo.working_tree_dir, c.oem)
        if tracker_file is not None:
            c_gapps_dict = c.get_gapps_dict()
            if return_dict:
                return c_gapps_dict
            if c_gapps_dict is not None:
                Json.write_dict_to_file(c_gapps_dict, tracker_file)
                if isexists:
                    print(f"Updating {tracker_file}")
                    tracker_repo.update_repo_changes("Synced with Cheetah Tracker for " + android_version)
                else:
                    print("File is empty!")
                    tracker_repo.update_repo_changes(
                        "Initial commit for Cheetah tracker for android version: " + android_version)
                return tracker_file
            else:
                print("Failed to get Cheetah GApps Dict!")
                return None
        else:
            print("Cheetah Tracker is None!")
            return None

    @staticmethod
    def sync_with_evo_x_tracker(android_version, tracker_repo=None, appsets=None, return_dict=False):
        if tracker_repo is None:
            tracker_repo = GitOperations.setup_tracker_repo()
            if tracker_repo is None:
                print("Failed to setup tracker repo!")
                return None
        evo = EvoX(android_version)
        tracker_file, isexists = Operations.get_tracker(android_version, tracker_repo.working_tree_dir, evo.oem)
        if tracker_file is not None:
            evo_gapps_dict = evo.get_evo_x_dict()
            if return_dict:
                return evo_gapps_dict
            if evo_gapps_dict is not None:
                Json.write_dict_to_file(evo_gapps_dict, tracker_file)
                if isexists:
                    print(f"Updating {tracker_file}")
                    tracker_repo.update_repo_changes("Synced with Evo X Tracker for " + android_version)
                else:
                    print("File is empty!")
                    tracker_repo.update_repo_changes(
                        "Initial commit for Evo X tracker for android version: " + android_version)
                return tracker_file
            else:
                print("Evo X Tracker is None!")
                return None
        else:
            print("Evo X Tracker is None!")
            return None

    @staticmethod
    def sync_with_pixel_experience_tracker(android_version, tracker_repo=None, appsets=None, return_dict=False):
        if tracker_repo is None:
            tracker_repo = GitOperations.setup_tracker_repo()
            if tracker_repo is None:
                print("Failed to setup tracker repo!")
                return None
        pe = PixelExperience(android_version)
        if not pe.is_supported:
            print(f"{android_version} is not supported by at the moment!")
            return None
        tracker_file, isexists = Operations.get_tracker(android_version, tracker_repo.working_tree_dir, pe.oem)
        if tracker_file is not None:
            pixel_experience_dict = pe.get_pixel_experience_dict()
            if return_dict:
                return pixel_experience_dict
            if pixel_experience_dict is not None:
                Json.write_dict_to_file(pixel_experience_dict, tracker_file)
                if isexists:
                    print(f"Updating {tracker_file}")
                    tracker_repo.update_repo_changes("Synced with PixelExperience Tracker")
                else:
                    print("File is empty!")
                    tracker_repo.update_repo_changes("Initial commit for Pixel Experience tracker")
                return tracker_file
            else:
                print("Pixel Experience Tracker is None!")
                return None
        else:
            print("Pixel Experience Tracker is None!")
            return None

    @staticmethod
    def sync_with_apk_mirror(android_version, tracker_repo=None, appsets=None, return_dict=False):
        if tracker_repo is None:
            tracker_repo = GitOperations.setup_tracker_repo()
            if tracker_repo is None:
                print("Failed to setup tracker repo!")
                return None
        am = ApkMirror(android_version)
        apk_mirror_tracker, isexists = Operations.get_tracker(android_version, tracker_repo.working_tree_dir, am.oem)
        if apk_mirror_tracker is not None:
            appset_list = []
            if appsets is not None:
                for appset in appsets:
                    for app in NikGappsPackages.get_packages(appset):
                        appset_list.append(app)
            am_dict = am.get_apk_mirror_dict(
                appset_list if appsets is not None else NikGappsPackages.get_packages("all"))
            if return_dict:
                return am_dict
            if am_dict is not None:
                Json.write_dict_to_file(am_dict, apk_mirror_tracker)
                if isexists:
                    print(f"Updating {apk_mirror_tracker}")
                    tracker_repo.update_repo_changes("Synced with Apk Mirror Tracker for " + android_version)
                else:
                    print("File is empty!")
                    tracker_repo.update_repo_changes(
                        "Initial commit for Apk Mirror tracker for android version: " + android_version)
                return apk_mirror_tracker
            else:
                print("Failed to get Apk Mirror Dict!")
                return None
        else:
            print("Apk Mirror Tracker is None!")
            return None
