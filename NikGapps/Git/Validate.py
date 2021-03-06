import os
from NikGapps.Git.PullRequest import PullRequest


class Validate:

    @staticmethod
    def pull_request(pr: PullRequest):
        failure_reason = []
        files_changed = pr.get_files_changed()
        total = len(files_changed)
        print("Total files changed: " + str(total))
        for i in range(0, total):
            print()
            file_name = str(files_changed[i]["filename"])
            print("Validating: " + file_name)
            print("- checking file name")
            if not file_name.endswith(".config"):
                failure_reason.append(f"{file_name} doesn't have .config extension, we only accept config files!")
            print("- checking if android version is present")
            if not (file_name.startswith("10" + os.path.sep) or file_name.startswith("11" + os.path.sep)):
                failure_reason.append(f"{file_name} must be part of Android Version folder, not outside of it!")
            print("- checking file status")
            file_status = str(files_changed[i]["status"])
            if not file_status.__eq__("added"):
                failure_reason.append(
                    f"We cannot merge the changes automatically since {file_name} is either modified or removed, "
                    "Wait for someone to manually review!")
        return failure_reason
