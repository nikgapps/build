from NikGappsPackages import NikGappsPackages
from Config import FRESH_BUILD
from Config import SIGN_ZIP
from Config import SEND_ZIP_DEVICE
from Config import SIGN_PACKAGE
import Config
from Config import UPLOAD_FILES
from .ZipOp import ZipOp
from .FileOp import FileOp
from .C import C
from .Assets import Assets
from .Package import Package
from .AppSet import AppSet
from .Cmd import Cmd
import os
from NikGapps.Helper.Upload import Upload


class Export:
    def __init__(self, file_name):
        self.file_name = file_name
        self.z = ZipOp(file_name)

    def zip(self, app_set_list, config_string):
        total_packages = 0
        print_progress = ""
        start_time = C.start_of_function()
        file_sizes = ""
        zip_execution_status = False
        try:
            app_set_count = len(app_set_list)
            app_set_index = 1
            C.telegram.message("- Gapps is building...")
            for app_set in app_set_list:
                app_set: AppSet
                app_set_progress = round(float(100 * app_set_index / app_set_count))
                C.telegram.message(
                    f"- Gapps ({app_set_index}/{app_set_count} appsets) is building... {str(app_set_progress)}% done",
                    replace_last_message=True)
                package_count = len(app_set.package_list)
                package_index = 0
                for pkg in app_set.package_list:
                    pkg_size = 0
                    # Creating <Packages>.zip for all the packages
                    pkg: Package
                    package_progress = round(float(100 * package_index / package_count))
                    pkg_zip_path = C.temp_packages_directory + C.dir_sep + "Packages" + C.dir_sep + str(
                        pkg.package_title) + ".zip"
                    pkg_txt_path = C.temp_packages_directory + C.dir_sep + "Packages" + C.dir_sep + str(
                        pkg.package_title) + ".txt"
                    print_value = "AppSet (" + str(
                        app_set_progress) + "%): " + app_set.title + " Zipping (" + str(
                        package_progress) + "%): " + pkg.package_title
                    print(print_value)
                    print_progress = print_progress + "\n" + print_value
                    file_exists = FileOp.file_exists(pkg_zip_path)
                    txt_file_exists = FileOp.file_exists(pkg_txt_path)
                    old_file = True if (
                            file_exists and C.get_mtime(pkg_zip_path) < C.local_datetime) else False
                    if (FRESH_BUILD and old_file) or (not file_exists) or (not txt_file_exists):
                        zpkg = ZipOp(pkg_zip_path)
                        file_index = 1
                        for x in pkg.file_dict:
                            file_index = file_index + 1
                            pkg_size = pkg_size + C.get_file_bytes(x)
                            zpkg.writefiletozip(x, str(x)[str(x).find("___"):].replace("\\", "/"))
                        if pkg.clean_flash_only:
                            zpkg.writestringtozip("", "___etc___permissions/" + pkg.package_title + ".prop")
                        pkg.pkg_size = pkg_size
                        zpkg.writestringtozip(pkg.get_installer_script(str(pkg_size)), "installer.sh")
                        zpkg.writestringtozip(pkg.get_uninstaller_script(), "uninstaller.sh")
                        zpkg.close()
                        FileOp.write_string_file(str(pkg_size), pkg_txt_path)
                        if SIGN_PACKAGE:
                            cmd = Cmd()
                            output_list = cmd.sign_zip_file(pkg_zip_path)
                            for output in output_list:
                                if output.__eq__("Success!"):
                                    pkg_zip_path = pkg_zip_path[:-4] + "-signed.zip"
                                    os.rename(pkg_zip_path, pkg_zip_path[:-11] + ".zip")
                                    pkg_zip_path = pkg_zip_path[:-11] + ".zip"
                                    print("The zip signed successfully: " + pkg_zip_path)
                    else:
                        print(f"Using cached package: {C.get_base_name(pkg_zip_path)}")
                        for size_on_file in FileOp.read_string_file(pkg_txt_path):
                            pkg_size = size_on_file
                            pkg.pkg_size = pkg_size
                    self.z.writefiletozip(pkg_zip_path,
                                          "AppSet/" + str(app_set.title) + "/" + str(pkg.package_title) + ".zip")
                    package_index = package_index + 1
                    total_packages += 1
                    file_sizes = file_sizes + str(pkg.package_title) + "=" + str(pkg_size) + "\n"
                app_set_index = app_set_index + 1
            # Writing additional script files to the zip
            self.z.writestringtozip(self.get_installer_script(total_packages, app_set_list), "common/install.sh")
            self.z.writestringtozip("#MAGISK", C.meta_inf_dir + "updater-script")
            self.z.writefiletozip(Assets.magisk_update_binary, C.meta_inf_dir + "update-binary")
            self.z.writestringtozip(config_string, "afzc/nikgapps.config")
            debloater_config_lines = ""
            for line in Assets.get_string_resource(Assets.debloater_config):
                debloater_config_lines += line
            self.z.writestringtozip(debloater_config_lines, "afzc/debloater.config")
            self.z.writefiletozip(Assets.changelog, "changelog.yaml")
            self.z.writefiletozip(Assets.addon_path, "common/addon")
            self.z.writefiletozip(Assets.header_path, "common/header")
            self.z.writefiletozip(Assets.functions_path, "common/functions")
            self.z.writestringtozip(file_sizes, "common/file_size")
            self.z.writefiletozip(Assets.nikgapps_functions, "common/nikgapps_functions.sh")
            self.z.writefiletozip(Assets.mount_path, "common/mount.sh")
            self.z.writefiletozip(Assets.unmount_path, "common/unmount.sh")
            self.z.writestringtozip(self.get_customize_sh(self.file_name), "customize.sh")
            self.z.writefiletozip(Assets.module_path, "module.prop")
            self.z.writefiletozip(Assets.busybox, "busybox")
            zip_execution_status = True
            print('The zip ' + self.file_name + ' is created successfully!')
        except Exception as e:
            print("Exception occurred while creating the zip " + str(e))
        finally:
            self.z.close()
            time_taken = C.end_of_function(start_time, "Total time taken to build the zip")
            C.telegram.message("- Completed in: " + str(round(time_taken)) + " seconds")
            file_name = self.file_name
            if SIGN_PACKAGE:
                # it means we already signed the packages, now, we just need to rename the package to file-signed.zip
                FileOp.remove_file(file_name[:-4] + "-signed.zip")
                os.rename(file_name, file_name[:-4] + "-signed.zip")
                file_name = file_name[:-4] + "-signed.zip"
                print("File renamed to: " + file_name)
            elif SIGN_ZIP:
                start_time = C.start_of_function()
                print('Signing The Zip')
                C.telegram.message("- The zip is Signing...")
                # the issue (cannot access class sun.security.pkcs.SignerInfo) is pending with Java 17
                # https://intellij-support.jetbrains.com/hc/en-us/community/posts/5153987456018-Java-17-cannot-access-class-sun-security-pkcs-PKCS7
                zip_execution_status = False
                cmd = Cmd()
                output_list = cmd.sign_zip_file(file_name)
                for output in output_list:
                    if output.__eq__("Success!"):
                        file_name = file_name[:-4] + "-signed.zip"
                        print("The zip signed successfully: " + file_name)
                        zip_execution_status = True
                    elif output.startswith("Exception occurred while executing"):
                        print("The zip could not be signed: " + output)
                        C.telegram.message("- The zip could not be signed: " + output)
                time_taken = C.end_of_function(start_time, "Total time taken to sign the zip")
                if zip_execution_status:
                    C.telegram.message("- The zip signed in: " + str(round(time_taken)) + " seconds",
                                       replace_last_message=True)
            if SEND_ZIP_DEVICE:
                start_time = C.start_of_function()
                cmd = Cmd()
                device_path = "/sdcard/Afzc-" + str(
                    C.android_version_folder) + "/" + C.current_time + "/" + C.get_base_name(
                    file_name)
                message = f"Sending {C.get_base_name(file_name)} to device at: " + device_path
                print(message)

                cmd.push_package(file_name, device_path)
                C.end_of_function(start_time, "Total time taken to send the zip to device")
            return file_name, zip_execution_status

    @staticmethod
    def get_installer_script(total_packages, app_set_list):
        delem = ","
        installer_script_path_string = "#!/sbin/sh\n"
        installer_script_path_string += "# Shell Script EDIFY Replacement\n\n"
        progress_max = 0.9
        progress_per_package = 0
        if total_packages > 0:
            progress_per_package = round(progress_max / total_packages, 2)
        install_progress = 0
        installer_script_path_string += f"ProgressBarValues=\"\n"
        for app_set in app_set_list:
            for pkg in app_set.package_list:
                install_progress += progress_per_package
                if install_progress > 1.0:
                    install_progress = 1.0
                installer_script_path_string += f"{pkg.package_title}={str(round(install_progress, 2))}\n"
        installer_script_path_string += "\"\n\n"
        for app_set in app_set_list:
            installer_script_path_string += f"{app_set.title}=\"\n"
            for pkg in app_set.package_list:
                installer_script_path_string += f"{pkg.package_title}{delem}{pkg.pkg_size}{delem}{pkg.partition}\n"
            installer_script_path_string += "\"\n\n"

        for app_set in app_set_list:
            installer_script_path_string += "install_app_set \"" + app_set.title + "\" " \
                                                                                   "\"$" + app_set.title + "\"\n"

        installer_script_path_string += "\nset_progress 1.00" + "\n\n"
        installer_script_path_string += "exit_install" + "\n\n"
        return installer_script_path_string

    @staticmethod
    def get_customize_sh(file_name):
        customize_path_string = "actual_file_name=" + os.path.basename(os.path.splitext(file_name)[0]) + "\n"
        lines = Assets.get_string_resource(Assets.customize_path)
        for line in lines:
            customize_path_string += line
        return customize_path_string
