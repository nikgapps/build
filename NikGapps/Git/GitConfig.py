import os

git_token_admin = os.environ.get('auth')
if git_token_admin is None:
    git_token_admin = ""

owner = "nikgapps"
repo = "config"
deploy_repo = "deploy"
