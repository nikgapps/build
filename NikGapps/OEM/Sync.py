from NikGapps.OEM.Operations import Operations


class Sync:
    def __init__(self, list_of_supported_appsets, tracker_repo):
        self.appsets = list_of_supported_appsets
        self.tracker_repo = tracker_repo

    def do(self, android_version, list_of_supported_oems=None):
        list_of_appsets = self.appsets
        if list_of_supported_oems is None:
            list_of_supported_oems, list_of_appsets = Operations.get_oems_from_controller(android_version,
                                                                                          self.tracker_repo)
        for oem in list_of_supported_oems:
            Operations.sync_tracker(android_version=android_version, oem=oem, appsets=list_of_appsets,
                                    tracker_repo=self.tracker_repo)
        Operations.sync_with_nikgapps_tracker(android_version, self.tracker_repo)
