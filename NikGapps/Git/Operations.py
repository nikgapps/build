from NikGapps.Helper import Constants, Git, FileOp


class Operations:

    @staticmethod
    def setup_tracker_repo():
        repo_name = "git@github.com:nikgapps/tracker.git"
        repo_dir = Constants.pwd + Constants.dir_sep + "tracker"
        print()
        print("Repo Dir: " + repo_dir)

        tracker_repo = Git(repo_dir)
        tracker_repo.clone_repo(repo_name)
        return tracker_repo