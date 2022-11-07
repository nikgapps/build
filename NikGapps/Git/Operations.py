from NikGapps.Helper import C, Git, FileOp


class Operations:

    @staticmethod
    def setup_tracker_repo():
        repo_name = "git@github.com:nikgapps/tracker.git"
        repo_dir = C.pwd + C.dir_sep + "tracker"
        print()
        print("Repo Dir: " + repo_dir)

        tracker_repo = Git(repo_dir)
        result = tracker_repo.clone_repo(repo_name)
        return tracker_repo if result else None
