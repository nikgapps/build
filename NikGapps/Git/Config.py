import os

git_token_admin = os.environ.get('auth')
if git_token_admin is None:
    git_token_admin = ""

owner = "nikgapps"
repo = "config"

display_response = os.environ['DISPLAY_RESPONSE']
if display_response is None:
    display_response = ""
elif str(display_response).__eq__("1"):
    display_response = True
else:
    display_response = False
