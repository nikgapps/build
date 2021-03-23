# The android version that we're targeting this application to run
TARGET_ANDROID_VERSION = 11

# Release type differentiates the experimental and stable features
# Possible values are [ 'production', 'development' ]
RELEASE_TYPE = "production"

# Possible Values are ['core', 'basic', 'omni', 'stock', 'full', 'ultra', 'addons', 'addonsets']
BUILD_PACKAGE_LIST = ['core', 'basic', 'omni', 'stock', 'full', 'addons', 'addonsets']

if TARGET_ANDROID_VERSION == 10:
    BUILD_PACKAGE_LIST.append("go")

# Send the zip to device after creation, Possible values are True and False
SEND_ZIP_DEVICE = False

# This will create a Debloater Zip
CREATE_DEBLOATER_ZIP = True

# This will allow the program to sign the zip
SIGN_ZIP = True
# This will allow the program to sign the individual packages
SIGN_PACKAGE = False
if RELEASE_TYPE.__eq__("production"):
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
if RELEASE_TYPE.__eq__("production"):
    DEBUG_MODE = False

# True if we want the files to upload as soon as they get created
UPLOAD_FILES = False

# Release day can be any of the 7 days
RELEASE_DAY = "Sat"

# Override the execution if we re-trigger the workflow
OVERRIDE_RELEASE = False

# Git Check enables controlled releases.
# If this is set to True, new release will only happen when there is a change in the source repo or apk is updated
GIT_CHECK = False
