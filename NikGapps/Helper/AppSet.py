from NikGapps.Helper.Package import Package


class AppSet:

    def __init__(self, name, gapps_list=None):
        self.title = name
        if gapps_list is None:
            self.package_list = []
        else:
            self.package_list = gapps_list
        self.config_note = ""

    def add_package(self, pkg: Package):
        self.package_list.append(pkg)
