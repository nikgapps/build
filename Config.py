import os

ANDROID_VERSIONS = {
    '10': {'sdk': '29', 'code': 'Q'}
    , '11': {'sdk': '30', 'code': 'R'}
    , '12': {'sdk': '31', 'code': 'S'}
    , '12.1': {'sdk': '32', 'code': 'SL'}
    , '13': {'sdk': '33', 'code': 'T'}
    }

# The android version that we're targeting this application to run
TARGET_ANDROID_VERSION = 13

# Release type defines the release
# Possible values are [ 'canary', 'stable' ]
RELEASE_TYPE = "stable"
release_type = os.environ.get('RELEASE_TYPE')
if release_type is not None:
    RELEASE_TYPE = release_type

# Environment type differentiates the experimental and stable features
# Possible values are [ 'production', 'development' ]
ENVIRONMENT_TYPE = "production"
environment_type = os.environ.get('ENVIRONMENT_TYPE')
if environment_type is not None:
    ENVIRONMENT_TYPE = environment_type

# Possible Values are ['go', 'core', 'basic', 'omni', 'stock', 'full', 'addons', 'addonsets']
BUILD_PACKAGE_LIST = ['go', 'core', 'basic', 'omni', 'stock', 'full', 'addons', 'addonsets']

# Send the zip to device after creation, Possible values are True and False
SEND_ZIP_DEVICE = True
if ENVIRONMENT_TYPE.__eq__("production"):
    SEND_ZIP_DEVICE = False

# This will create a Debloater Zip
CREATE_DEBLOATER_ZIP = True

# This will allow the program to sign the zip
SIGN_ZIP = True
# This will allow the program to sign the individual packages
SIGN_PACKAGE = False
if ENVIRONMENT_TYPE.__eq__("production"):
    SIGN_ZIP = True
    SIGN_PACKAGE = False

# if we're signing the packages, we don't need to sign the zip
if SIGN_PACKAGE:
    SIGN_ZIP = False

# When Fresh Build is True, the installer will freshly build the zip (Comparatively Slower)
# When Fresh Build is False, the installer picks up existing zip and builds gapps package (Faster)
FRESH_BUILD = True

# DEBUG_MODE will be helpful in printing more stuff so program can be debugged
DEBUG_MODE = True
if ENVIRONMENT_TYPE.__eq__("production"):
    DEBUG_MODE = False

# True if we want the files to upload as soon as they get created
UPLOAD_FILES = True

# Release day can be any of the 7 days
RELEASE_DAY = "Sat"

# Override the execution if we re-trigger the workflow
OVERRIDE_RELEASE = False

# Git Check enables controlled releases.
# If this is set to True, new release will only happen when there is a change in the source repo or apk is updated
GIT_CHECK = True

# Enabling this will enable the feature of building NikGapps using config file
BUILD_CONFIG = True

# Possible Values are ['fetch', 'build']
# PROJECT_MODE = "fetch"
PROJECT_MODE = "build"

# This will help fetch the files which requires root access such as overlay files
ADB_ROOT_ENABLED = False

# Fetch Package is the package you wish to pull from your device
# Possible Values are ['core', 'basic', 'omni', 'stock', 'full', 'ultra', 'addons', 'addonsets', '<addon>'
# (for e.g 'YouTube')]
FETCH_PACKAGE = "core"

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
