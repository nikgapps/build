from NikGappsPackages import NikGappsPackages
from Config import FRESH_BUILD
from Config import SIGN_ZIP
from Config import SEND_ZIP_DEVICE
from Config import SIGN_PACKAGE
import Config
from Config import UPLOAD_FILES
from .AddonSet import AddonSet
from .ZipOp import ZipOp
from .FileOp import FileOp
from .Constants import Constants
from .Assets import Assets
from .Package import Package
from .AppSet import AppSet
from .Cmd import Cmd
import os
from NikGapps.Helper.Upload import Upload
import platform


class Export:
    def __init__(self, file_name):
        self.file_name = file_name
        self.z = ZipOp(file_name)

    def zip(self, app_set_list, sent_message=None):
        total_packages = 0
        print_progress = ""
        start_time = Constants.start_of_function()
        file_sizes = ""
        zip_execution_status = False
        try:
            app_set_count = len(app_set_list)
            app_set_index = 1
            for app_set in app_set_list:
                app_set: AppSet
                app_set_progress = round(float(100 * app_set_index / app_set_count))
                package_count = len(app_set.package_list)
                package_index = 0
                for pkg in app_set.package_list:
                    pkg_size = 0
                    # Creating <Packages>.zip for all the packages
                    pkg: Package
                    package_progress = round(float(100 * package_index / package_count))
                    pkg_zip_path = Constants.temp_packages_directory + Constants.dir_sep + "Packages" + Constants.dir_sep + str(
                        pkg.package_title) + ".zip"
                    print_value = "AppSet (" + str(
                        app_set_progress) + "%): " + app_set.title + " Zipping (" + str(
                        package_progress) + "%): " + pkg.package_title
                    print(print_value)
                    print_progress = print_progress + "\n" + print_value
                    file_exists = FileOp.file_exists(pkg_zip_path)
                    old_file = True if (
                            file_exists and Constants.get_mtime(pkg_zip_path) < Constants.local_datetime) else False
                    if (FRESH_BUILD and old_file) or (not file_exists):
                        zpkg = ZipOp(pkg_zip_path)
                        file_index = 1
                        if sent_message is not None:
                            try:
                                sent_message.edit_text(print_progress)
                            except Exception as e:
                                print(str(e))
                        for x in pkg.file_dict:
                            file_index = file_index + 1
                            pkg_size = pkg_size + Constants.get_file_bytes(x)
                            zpkg.writefiletozip(x, str(x)[str(x).find("___"):].replace("\\", "/"))
                        zpkg.writestringtozip(pkg.get_installer_script(), "installer.sh")
                        zpkg.close()
                        if SIGN_PACKAGE:
                            cmd = Cmd()
                            output_list = cmd.sign_zip_file(pkg_zip_path)
                            for output in output_list:
                                if output.__eq__("Success!"):
                                    pkg_zip_path = pkg_zip_path[:-4] + "-signed.zip"
                                    os.rename(pkg_zip_path, pkg_zip_path[:-11] + ".zip")
                                    pkg_zip_path = pkg_zip_path[:-11] + ".zip"
                                    print("The zip signed successfully: " + pkg_zip_path)
                                    if sent_message is not None:
                                        sent_message.edit_text(
                                            "The zip signed successfully: " + Constants.get_base_name(pkg_zip_path))
                    self.z.writefiletozip(pkg_zip_path,
                                          "AppSet/" + str(app_set.title) + "/" + str(pkg.package_title) + ".zip")
                    package_index = package_index + 1
                    total_packages += 1
                    file_sizes = file_sizes + str(pkg.package_title) + "=" + str(pkg_size) + "\n"
                app_set_index = app_set_index + 1
            # Writing additional script files to the zip
            self.z.writestringtozip(self.get_updater_script(total_packages, app_set_list), "common/install.sh")
            self.z.writestringtozip("#MAGISK", Constants.meta_inf_dir + "updater-script")
            self.z.writefiletozip(Assets.magisk_update_binary, Constants.meta_inf_dir + "update-binary")
            self.z.writestringtozip(self.get_nikgapps_config(), "afzc/nikgapps.config")
            debloater_config_lines = ""
            for line in Assets.get_string_resource(Assets.debloater_config):
                debloater_config_lines += line
            self.z.writestringtozip(debloater_config_lines, "afzc/debloater.config")
            self.z.writefiletozip(Assets.changelog, "changelog.yaml")
            self.z.writefiletozip(Assets.addon_path, "common/addon")
            self.z.writefiletozip(Assets.addon_sh_path, "common/nikgapps.sh")
            self.z.writefiletozip(Assets.header_path, "common/header")
            self.z.writefiletozip(Assets.functions_path, "common/functions")
            self.z.writestringtozip(file_sizes, "common/file_size")
            self.z.writefiletozip(Assets.nikgapps_functions, "common/nikgapps_functions.sh")
            self.z.writefiletozip(Assets.mount_path, "common/mount.sh")
            self.z.writefiletozip(Assets.unmount_path, "common/unmount.sh")
            self.z.writefiletozip(Assets.device_path, "common/device.sh")
            self.z.writestringtozip(self.get_customize_sh(self.file_name), "customize.sh")
            self.z.writefiletozip(Assets.module_path, "module.prop")
            self.z.writefiletozip(Assets.busybox, "busybox")
            zip_execution_status = True
            print('The zip ' + self.file_name + ' is created successfully!')
            if sent_message is not None:
                sent_message.edit_text(
                    "The zip " + Constants.get_base_name(self.file_name) + " is created successfully!")
        except Exception as e:
            print("Exception occurred while creating the zip " + str(e))
        finally:
            self.z.close()
            Constants.end_of_function(start_time, "Total time taken to build the zip")
            file_name = self.file_name
            if SIGN_PACKAGE:
                # it means we already signed the packages, now, we just need to rename the package to file-signed.zip
                FileOp.remove_file(file_name[:-4] + "-signed.zip")
                os.rename(file_name, file_name[:-4] + "-signed.zip")
                file_name = file_name[:-4] + "-signed.zip"
                print("File renamed to: " + file_name)
            elif SIGN_ZIP:
                start_time = Constants.start_of_function()
                print('Signing The Zip')
                zip_execution_status = False
                if sent_message is not None:
                    sent_message.edit_text("Signing The Zip")
                cmd = Cmd()
                output_list = cmd.sign_zip_file(file_name)
                for output in output_list:
                    if output.__eq__("Success!"):
                        file_name = file_name[:-4] + "-signed.zip"
                        print("The zip signed successfully: " + file_name)
                        zip_execution_status = True
                        if sent_message is not None:
                            sent_message.edit_text("The zip signed successfully: " + Constants.get_base_name(file_name))
                Constants.end_of_function(start_time, "Total time taken to sign the zip")
            if SEND_ZIP_DEVICE:
                start_time = Constants.start_of_function()
                cmd = Cmd()
                device_path = "/sdcard/Afzc-" + str(
                    Constants.android_version_folder) + "/" + Constants.current_time + "/" + Constants.get_base_name(
                    file_name)
                message = f"Sending {Constants.get_base_name(file_name)} to device at: " + device_path
                print(message)
                if sent_message is not None:
                    sent_message.edit_text(message)

                cmd.push_package(file_name, device_path)
                if sent_message is not None:
                    sent_message.edit_text("Sent the zip!")
                Constants.end_of_function(start_time, "Total time taken to send the zip to device")
            system_name = platform.system()
            if system_name != "Windows" and UPLOAD_FILES:
                start_time = Constants.start_of_function()
                # make the connection and initialize the parameters
                file_type = "gapps"
                if Constants.get_base_name(file_name).__contains__("Addon"):
                    file_type = "addons"
                elif Constants.get_base_name(file_name).__contains__("Debloater"):
                    file_type = "debloater"
                u = Upload()
                zip_execution_status = False
                # proceed only if the connection is successful
                if u.successful_connection:
                    # check if directory exists, if it does, we're good to upload the file
                    cd = u.get_cd_with_date(Config.TARGET_ANDROID_VERSION, file_type)
                    dir_exists = u.cd(cd)
                    if not dir_exists:
                        print(str(cd) + " doesn't exist!")
                        # make the folder with current date if the directory doesn't exist
                        u.make_folder(Config.TARGET_ANDROID_VERSION, file_type)
                        # try to cd again
                        dir_exists = u.cd(u.get_cd_with_date(Config.TARGET_ANDROID_VERSION, file_type))
                    # if the directory exists, we can upload the file
                    if dir_exists:
                        print("uploading " + file_name + " ...")
                        u.upload_file(file_name)
                        print("uploading file finished...")
                        zip_execution_status = True
                    else:
                        print("The directory doesn't exist!")
                else:
                    print("The Connection Failed!")
                # make sure we close the connection
                u.close()
                Constants.end_of_function(start_time, "Total time taken to upload the file")
            return zip_execution_status

    @staticmethod
    def get_nikgapps_config():
        nikgapps_config_lines = ""
        for line in Assets.get_string_resource(Assets.nikgapps_config):
            nikgapps_config_lines += line
        for app_set in NikGappsPackages.get_packages("full"):
            if len(app_set.package_list) > 1:
                nikgapps_config_lines += "\n# Set " + app_set.title + "=0 if you want to skip installing all " \
                                                                      "packages belonging to " \
                                                                      "" + app_set.title + " Package\n"
                nikgapps_config_lines += app_set.title + "=" + str(1) + "\n"
                if str(os.environ.get('pkg_type')).__eq__("config"):
                    for pkg in app_set.package_list:
                        nikgapps_config_lines += ">>" + pkg.package_title + "=" + str(1) + "\n"
                else:
                    for pkg in app_set.package_list:
                        nikgapps_config_lines += ">>" + pkg.package_title + "=" + str(pkg.enabled) + "\n"
                nikgapps_config_lines += "\n"
            else:
                if str(os.environ.get('pkg_type')).__eq__("config"):
                    for pkg in app_set.package_list:
                        nikgapps_config_lines += pkg.package_title + "=" + str(1) + "\n"
                else:
                    for pkg in app_set.package_list:
                        nikgapps_config_lines += pkg.package_title + "=" + str(pkg.enabled) + "\n"
        for app_set in NikGappsPackages.get_packages("go"):
            if len(app_set.package_list) > 1:
                nikgapps_config_lines += "# Set " + app_set.title + "=0 if you want to skip installing all " \
                                                                    "packages belonging to " \
                                                                    "" + app_set.title + " Package\n"
            nikgapps_config_lines += app_set.title + "=" + str(1) + "\n"
        nikgapps_config_lines += "\n"
        nikgapps_config_lines += "# Following are the Addon packages NikGapps supports\n"
        for app_set in AddonSet.get_addon_packages():
            nikgapps_config_lines += app_set.title + "=" + str(1) + "\n"
        return nikgapps_config_lines

    @staticmethod
    def get_updater_script(total_packages, app_set_list):
        updater_script_path_string = "#!/sbin/sh\n"
        updater_script_path_string += "# Shell Script EDIFY Replacement\n\n"
        progress_max = 0.9
        progress_per_package = 0
        if total_packages > 0:
            progress_per_package = round(progress_max / total_packages, 2)
        install_progress = 0
        # Script to Install the ApPSets
        for app_set in app_set_list:
            if len(app_set.package_list) > 1:
                updater_script_path_string += "if [ $(initialize_app_set \"" + app_set.title + "\") = \"1\" ]; then\n"
                # Script to Install the Packages
                for pkg in app_set.package_list:
                    install_progress += progress_per_package
                    if install_progress > 1.0:
                        install_progress = 1.0
                    updater_script_path_string += "  install_the_package \"" + str(app_set.title) + "\" \"" + str(
                        pkg.package_title) + "\"\n"
                    updater_script_path_string += "  set_progress " + str(round(install_progress, 2)) + "\n"
                updater_script_path_string += "else\n"
                updater_script_path_string += "  ui_print \"x Skipping " + str(app_set.title) + "\"\n"
                updater_script_path_string += "fi\n"
            else:
                # Script to Install the Packages
                for pkg in app_set.package_list:
                    install_progress += progress_per_package
                    if install_progress > 1.0:
                        install_progress = 1.0
                    updater_script_path_string += "  install_the_package \"" + str(app_set.title) + "\" \"" + str(
                        pkg.package_title) + "\"\n"
                    updater_script_path_string += "  set_progress " + str(round(install_progress, 2)) + "\n"

        updater_script_path_string += "\nset_progress 1.00" + "\n\n"
        updater_script_path_string += "exit_install" + "\n\n"
        return updater_script_path_string

    @staticmethod
    def get_customize_sh(file_name):
        customize_path_string = "actual_file_name=" + os.path.basename(os.path.splitext(file_name)[0]) + "\n"
        lines = Assets.get_string_resource(Assets.customize_path)
        for line in lines:
            customize_path_string += line
        return customize_path_string
