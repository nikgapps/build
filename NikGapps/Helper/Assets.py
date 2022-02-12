from .Constants import Constants
from .FileOp import FileOp
import os.path
import platform


class Assets:
    assets_folder = os.path.join(os.getcwd(), 'NikGapps', 'Assets')
    cwd = assets_folder + Constants.dir_sep
    system_name = platform.system()
    if system_name == "Windows":
        aapt_path = os.path.join(assets_folder, 'bin', system_name, 'aapt_64.exe')
        adb_path = os.path.join(assets_folder, 'bin', system_name, 'adb.exe')
    elif system_name == "Linux":
        aapt_path = "adb"
        adb_path = "aapt"
    elif system_name == "Darwin":
        aapt_path = "/Users/runner/Library/Android/sdk/build-tools/30.0.0/aapt"
        adb_path = "adb"
    else:
        aapt_path = "adb"
        adb_path = "aapt"
    addon_path = cwd + "addon"
    header_path = cwd + "header"
    functions_path = cwd + "functions.sh"
    addon_sh_path = cwd + "addon.sh"
    busybox = cwd + "busybox"
    file_sizes_path = cwd + "file_size.txt"
    mount_path = cwd + "mount.sh"
    unmount_path = cwd + "unmount.sh"
    nikgapps_functions = cwd + "nikgapps_functions.sh"
    update_script_path = cwd + "updater-script"
    nikgapps_config = cwd + "nikgapps.config"
    debloater_config = cwd + "debloater.config"
    installer_path = cwd + "installer"
    uninstaller_path = cwd + "uninstaller"
    changelog = cwd + "changelogs.yaml"
    sign_jar = os.path.join(assets_folder, "NikGappsZipSigner.jar")
    customize_path = cwd + "customize.sh"
    module_path = cwd + "module.prop"
    magisk_update_binary = cwd + "magisk-update-binary.sh"

    @staticmethod
    def get_string_resource(file_path):
        return FileOp.read_string_file(file_path)

    @staticmethod
    def get_binary_resource(file_path):
        return FileOp.read_binary_file(file_path)
