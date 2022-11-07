from NikGapps.Helper import C, Git, FileOp


class ConfigDirectory:

    def __init__(self, repo_dir=None):
        self.repo_name = "git@github.com:nikgapps/config.git"
        if repo_dir is not None:
            self.repo_dir = repo_dir
        else:
            self.repo_dir = C.pwd + C.dir_sep + "config"
        self.config_repo = Git(self.repo_dir)

    def setup(self, override_dir=True):
        branch = "main"
        if not self.config_repo.clone_repo(repo_url=self.repo_name, branch=branch, fresh_clone=override_dir):
            self.config_repo = None
        return self.config_repo

    def write_user_config(self, config_string, android_version, config_name):
        path = self.repo_dir + C.dir_sep + str(android_version) + C.dir_sep + config_name
        try:
            FileOp.write_string_in_lf_file(str_data=config_string, file_path=path)
        except Exception as e:
            print(e)
            path = None
        return path
