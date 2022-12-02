from NikGapps.OEM.Operations import Operations


class Sync:
    def __init__(self, list_of_supported_appsets):
        self.appsets = list_of_supported_appsets

    def do(self, tracker_repo, android_version, list_of_supported_oems=None):
        if list_of_supported_oems is None:
            list_of_supported_oems = Operations.get_oems_from_controller(android_version, tracker_repo)
        for oem in list_of_supported_oems:
            Operations.sync_tracker(android_version=android_version, oem=oem, tracker_repo=tracker_repo)
