from Config import TARGET_ANDROID_VERSION
from NikGapps.Helper import C
from NikGapps.Helper.AddonSet import AddonSet
from NikGapps.Helper.Package import Package
from NikGapps.Helper.AppSet import AppSet


class NikGappsPackages:
    all_packages = "full"

    @staticmethod
    def get_packages(package_type):
        if str(package_type).lower() == "go":
            return NikGappsPackages.get_go_package()
        if str(package_type).lower() == "core":
            return NikGappsPackages.get_core_package()
        if str(package_type).lower() == "basic":
            return NikGappsPackages.get_basic_package()
        if str(package_type).lower() == "omni":
            return NikGappsPackages.get_omni_package()
        if str(package_type).lower() == "stock":
            return NikGappsPackages.get_stock_package()
        if str(package_type).lower() == "full":
            return NikGappsPackages.get_full_package()
        if str(package_type).lower() == "all":
            all_package_list = []
            for app_set in NikGappsPackages.get_full_package():
                all_package_list.append(app_set)
            for app_set in NikGappsPackages.get_go_package():
                all_package_list.append(app_set)
            for app_set in AddonSet.get_addon_packages():
                all_package_list.append(app_set)
            return all_package_list
        if str(package_type).lower() == "addons":
            addon_set_list = AddonSet.get_addon_packages()
            return addon_set_list
        if str(package_type).lower() == "addonsets":
            addon_set_list = []
            for app_set in NikGappsPackages.get_full_package():
                if app_set.title in ['Core', 'Pixelize']:
                    continue
                addon_set_list.append(app_set)
            for app_set in NikGappsPackages.get_go_package():
                if app_set.title in ['CoreGo']:
                    continue
                addon_set_list.append(app_set)
            return addon_set_list
        else:
            addon_set_list = AddonSet.get_addon_packages(package_type)
            if addon_set_list is None:
                for app_set in NikGappsPackages.get_full_package():
                    if str(app_set.title).lower() == str(package_type).lower():
                        return [app_set]
                    elif len(app_set.package_list) > 1:
                        for package in app_set.package_list:
                            if str(package.package_title).lower() == str(package_type).lower():
                                return [AppSet(package.package_title, [package])]
                for app_set in NikGappsPackages.get_go_package():
                    if str(app_set.title).lower() == str(package_type).lower():
                        return [app_set]
                    elif len(app_set.package_list) > 1:
                        for package in app_set.package_list:
                            if str(package.package_title).lower() == str(package_type).lower():
                                return [AppSet(package.package_title, [package])]
                return [None]
            else:
                return addon_set_list

    @staticmethod
    def get_app_set(pkg: Package, title=None):
        if title is None:
            name = pkg.package_title
        else:
            name = title
        return AppSet(name, [pkg])

    @staticmethod
    def get_go_package():
        extra_files_go = Package("ExtraFilesGo", None, None)
        extra_files_go.additional_installer_script = """script_text="<permissions>
                            <!-- Shared library required on the device to get Google Dialer updates from
                                 Play Store. This will be deprecated once Google Dialer play store
                                 updates stop supporting pre-O devices. -->
                            <library name=\\"com.google.android.dialer.support\\"
                              file=\\"$install_partition/framework/com.google.android.dialer.support.jar\\" />

                            <!-- Starting from Android O and above, this system feature is required for
                                 getting Google Dialer play store updates. -->
                            <feature name=\\"com.google.android.apps.dialer.SUPPORTED\\" />
                            <!-- Feature for Google Dialer Call Recording -->
                            <feature name=\\"com.google.android.apps.dialer.call_recording_audio\\" />
                        </permissions>"
                        echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.dialer.support.xml
                        set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.dialer.support.xml"
                        installPath=$product_prefix"etc/permissions/com.google.android.dialer.support.xml"
                        echo "install=$installPath" >> $TMPDIR/addon/$packagePath
                        if [ -f "$install_partition/etc/permissions/com.google.android.dialer.support.xml" ]; then
                          addToPackageLog "- $install_partition/etc/permissions/com.google.android.dialer.support.xml Successfully Written!" "$package_title"
                        fi"""
        extra_files_go.additional_installer_script += """
                        script_text="<permissions>
                            <library name=\\"com.google.android.maps\\"
                                    file=\\"$install_partition/framework/com.google.android.maps.jar\\" />
                        </permissions>"
                        echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.maps.xml
                        set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.maps.xml"
                        installPath=$product_prefix"etc/permissions/com.google.android.maps.xml"
                        echo "install=$installPath" >> $TMPDIR/addon/$packagePath
                        if [ -f "$install_partition/etc/permissions/com.google.android.maps.xml" ]; then
                          addToPackageLog "- $install_partition/etc/permissions/com.google.android.maps.xml Successfully Written!" "$package_title"
                        fi"""
        extra_files_go.additional_installer_script += """
                                script_text="<permissions>
                    <library name=\\"com.google.widevine.software.drm\\"
                        file=\\"/system/product/framework/com.google.widevine.software.drm.jar\\"/>
                </permissions>"
                                echo -e "$script_text" > $install_partition/etc/permissions/com.google.widevine.software.drm.xml
                                set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.widevine.software.drm.xml"
                                installPath=$product_prefix"etc/permissions/com.google.widevine.software.drm.xml"
                                echo "install=$installPath" >> $TMPDIR/addon/$packagePath
                                if [ -f "$install_partition/etc/permissions/com.google.widevine.software.drm.xml" ]; then
                                  addToPackageLog "- $install_partition/etc/permissions/com.google.widevine.software.drm.xml Successfully Written!" "$package_title"
                                fi"""
        extra_files_go.additional_installer_script += """
                                script_text="<permissions>
                    <library name=\\"com.google.android.media.effects\\"
                            file=\\"$install_partition/framework/com.google.android.media.effects.jar\\" />

                </permissions>"
                                echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.media.effects.xml
                                set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.media.effects.xml"
                                installPath=$product_prefix"etc/permissions/com.google.android.media.effects.xml"
                                echo "install=$installPath" >> $TMPDIR/addon/$packagePath
                                if [ -f "$install_partition/etc/permissions/com.google.android.media.effects.xml" ]; then
                                  addToPackageLog "- $install_partition/etc/permissions/com.google.android.media.effects.xml Successfully Written!" "$package_title"
                                fi"""

        core_go = AppSet("CoreGo")
        core_go.add_package(extra_files_go)

        prebuiltgmscore = Package("PrebuiltGmsCore", "com.google.android.gms", C.is_priv_app, "GmsCore")
        prebuiltgmscore.delete("PrebuiltGmsCoreQt")
        prebuiltgmscore.delete("PrebuiltGmsCoreRvc")
        prebuiltgmscore.delete("GmsCore")
        prebuiltgmscore.additional_installer_script = """
    gms_optimization=$(ReadConfigValue "gms_optimization" "$nikgapps_config_file_name")
    [ -z "$gms_optimization" ] && gms_optimization=0
    if [ "$gms_optimization" = "1" ]; then
        sed -i '/allow-in-power-save package=\"com.google.android.gms\"/d' $install_partition/etc/permissions/*.xml
        sed -i '/allow-in-data-usage-save package=\"com.google.android.gms\"/d' $install_partition/etc/permissions/*.xml
        sed -i '/allow-unthrottled-location package=\"com.google.android.gms\"/d' $install_partition/etc/permissions/*.xml
        sed -i '/allow-ignore-location-settings package=\"com.google.android.gms\"/d' $install_partition/etc/permissions/*.xml
        addToPackageLog \"- Battery Optimization Done in $install_partition/etc/permissions/*.xml!\" "$package_title"
        sed -i '/allow-in-power-save package=\"com.google.android.gms\"/d' $install_partition/etc/sysconfig/*.xml
        sed -i '/allow-in-data-usage-save package=\"com.google.android.gms\"/d' $install_partition/etc/sysconfig/*.xml
        sed -i '/allow-unthrottled-location package=\"com.google.android.gms\"/d' $install_partition/etc/sysconfig/*.xml
        sed -i '/allow-ignore-location-settings package=\"com.google.android.gms\"/d' $install_partition/etc/sysconfig/*.xml
        addToPackageLog \"- Battery Optimization Done in $install_partition/etc/sysconfig/*.xml!\" "$package_title"
    else
        addToPackageLog "- Battery Optimization not Enabled" "$package_title"
    fi
        """
        core_go.add_package(prebuiltgmscore)

        phonesky = Package("Phonesky", "com.android.vending", C.is_priv_app, "GooglePlayStore")
        core_go.add_package(phonesky)

        googleservicesframework = Package("GoogleServicesFramework", "com.google.android.gsf", C.is_priv_app)
        core_go.add_package(googleservicesframework)

        googlecontactssyncadapter = Package("GoogleContactsSyncAdapter", "com.google.android.syncadapters.contacts",
                                            C.is_system_app)
        core_go.add_package(googlecontactssyncadapter)

        googlecalendarsync = Package("GoogleCalendarSyncAdapter", "com.google.android.syncadapters.calendar",
                                     C.is_system_app)
        core_go.add_package(googlecalendarsync)

        app_set_list = [core_go]

        google_go = Package("GoogleGo", "com.google.android.apps.searchlite", C.is_priv_app)
        app_set_list.append(AppSet("GoogleGo", [google_go]))

        google_assistant_go = Package("AssistantGo", "com.google.android.apps.assistant", C.is_priv_app)
        app_set_list.append(AppSet("AssistantGo", [google_assistant_go]))

        google_maps_go = Package("MapsGo", "com.google.android.apps.mapslite", C.is_system_app)
        app_set_list.append(AppSet("MapsGo", [google_maps_go]))

        navigation_go = Package("NavigationGo", "com.google.android.apps.navlite", C.is_system_app)
        app_set_list.append(AppSet("NavigationGo", [navigation_go]))

        gallery_go = Package("GalleryGo", "com.google.android.apps.photosgo", C.is_system_app)
        app_set_list.append(AppSet("GalleryGo", [gallery_go]))

        gmail_go = Package("GmailGo", "com.google.android.gm.lite", C.is_system_app)
        app_set_list.append(AppSet("GmailGo", [gmail_go]))

        return app_set_list

    @staticmethod
    def get_core_package():
        files = Package("ExtraFiles", None, None)
        files.additional_installer_script = """script_text="<permissions>
                    <!-- Shared library required on the device to get Google Dialer updates from
                         Play Store. This will be deprecated once Google Dialer play store
                         updates stop supporting pre-O devices. -->
                    <library name=\\"com.google.android.dialer.support\\"
                      file=\\"$install_partition/framework/com.google.android.dialer.support.jar\\" />

                    <!-- Starting from Android O and above, this system feature is required for
                         getting Google Dialer play store updates. -->
                    <feature name=\\"com.google.android.apps.dialer.SUPPORTED\\" />
                    <!-- Feature for Google Dialer Call Recording -->
                    <feature name=\\"com.google.android.apps.dialer.call_recording_audio\\" />
                </permissions>"
                echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.dialer.support.xml
                set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.dialer.support.xml"
                installPath=$product_prefix"etc/permissions/com.google.android.dialer.support.xml"
                echo "install=$installPath" >> $TMPDIR/addon/$packagePath
                if [ -f "$install_partition/etc/permissions/com.google.android.dialer.support.xml" ]; then
                  addToPackageLog "- $install_partition/etc/permissions/com.google.android.dialer.support.xml Successfully Written!" "$package_title"
                fi"""
        files.additional_installer_script += """
                script_text="<permissions>
                    <library name=\\"com.google.android.maps\\"
                            file=\\"$install_partition/framework/com.google.android.maps.jar\\" />
                </permissions>"
                echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.maps.xml
                set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.maps.xml"
                installPath=$product_prefix"etc/permissions/com.google.android.maps.xml"
                echo "install=$installPath" >> $TMPDIR/addon/$packagePath
                if [ -f "$install_partition/etc/permissions/com.google.android.maps.xml" ]; then
                  addToPackageLog "- $install_partition/etc/permissions/com.google.android.maps.xml Successfully Written!" "$package_title"
                fi"""
        files.additional_installer_script += """
                        script_text="<permissions>
            <library name=\\"com.google.widevine.software.drm\\"
                file=\\"/system/product/framework/com.google.widevine.software.drm.jar\\"/>
        </permissions>"
                        echo -e "$script_text" > $install_partition/etc/permissions/com.google.widevine.software.drm.xml
                        set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.widevine.software.drm.xml"
                        installPath=$product_prefix"etc/permissions/com.google.widevine.software.drm.xml"
                        echo "install=$installPath" >> $TMPDIR/addon/$packagePath
                        if [ -f "$install_partition/etc/permissions/com.google.widevine.software.drm.xml" ]; then
                          addToPackageLog "- $install_partition/etc/permissions/com.google.widevine.software.drm.xml Successfully Written!" "$package_title"
                        fi"""
        files.additional_installer_script += """
                        script_text="<permissions>
            <library name=\\"com.google.android.media.effects\\"
                    file=\\"$install_partition/framework/com.google.android.media.effects.jar\\" />

        </permissions>"
                        echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.media.effects.xml
                        set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.media.effects.xml"
                        installPath=$product_prefix"etc/permissions/com.google.android.media.effects.xml"
                        echo "install=$installPath" >> $TMPDIR/addon/$packagePath
                        if [ -f "$install_partition/etc/permissions/com.google.android.media.effects.xml" ]; then
                          addToPackageLog "- $install_partition/etc/permissions/com.google.android.media.effects.xml Successfully Written!" "$package_title"
                        fi"""

        # example of how to add files
        # files.predefined_file_list.append("framework/com.google.android.media.effects.jar")
        # files.predefined_file_list.append("lib64/libgdx.so")
        prebuiltgmscore = Package("PrebuiltGmsCore", "com.google.android.gms", C.is_priv_app, "GmsCore")
        prebuiltgmscore.delete("PrebuiltGmsCoreQt")
        prebuiltgmscore.delete("PrebuiltGmsCoreRvc")
        prebuiltgmscore.delete("GmsCore")
        prebuiltgmscore.additional_installer_script = """
    gms_optimization=$(ReadConfigValue "gms_optimization" "$nikgapps_config_file_name")
    [ -z "$gms_optimization" ] && gms_optimization=0
    if [ "$gms_optimization" = "1" ]; then
        sed -i '/allow-in-power-save package=\"com.google.android.gms\"/d' $install_partition/etc/permissions/*.xml
        sed -i '/allow-in-data-usage-save package=\"com.google.android.gms\"/d' $install_partition/etc/permissions/*.xml
        sed -i '/allow-unthrottled-location package=\"com.google.android.gms\"/d' $install_partition/etc/permissions/*.xml
        sed -i '/allow-ignore-location-settings package=\"com.google.android.gms\"/d' $install_partition/etc/permissions/*.xml
        addToPackageLog \"- Battery Optimization Done in $install_partition/etc/permissions/*.xml!\" "$package_title"
        sed -i '/allow-in-power-save package=\"com.google.android.gms\"/d' $install_partition/etc/sysconfig/*.xml
        sed -i '/allow-in-data-usage-save package=\"com.google.android.gms\"/d' $install_partition/etc/sysconfig/*.xml
        sed -i '/allow-unthrottled-location package=\"com.google.android.gms\"/d' $install_partition/etc/sysconfig/*.xml
        sed -i '/allow-ignore-location-settings package=\"com.google.android.gms\"/d' $install_partition/etc/sysconfig/*.xml
        addToPackageLog \"- Battery Optimization Done in $install_partition/etc/sysconfig/*.xml!\" "$package_title"
    else
        addToPackageLog "- Battery Optimization not Enabled" "$package_title"
    fi
                """
        phonesky = Package("Phonesky", "com.android.vending", C.is_priv_app, "GooglePlayStore")
        googleservicesframework = Package("GoogleServicesFramework", "com.google.android.gsf", C.is_priv_app)
        googlecontactssyncadapter = Package("GoogleContactsSyncAdapter", "com.google.android.syncadapters.contacts",
                                            C.is_system_app)
        googlecalendarsync = Package("GoogleCalendarSyncAdapter", "com.google.android.syncadapters.calendar",
                                     C.is_system_app)
        gapps_list = [files, phonesky, googleservicesframework, googlecontactssyncadapter, googlecalendarsync,
                      prebuiltgmscore]
        return [AppSet("Core", gapps_list)]

    @staticmethod
    def get_basic_package():
        app_set_list = NikGappsPackages.get_core_package()
        digital_wellbeing = Package("WellbeingPreBuilt", "com.google.android.apps.wellbeing", C.is_priv_app,
                                    "DigitalWellbeing")
        app_set_list.append(AppSet("DigitalWellbeing", [digital_wellbeing]))
        google_messages = Package("PrebuiltBugle", "com.google.android.apps.messaging", C.is_system_app,
                                  "GoogleMessages")
        google_messages.delete("RevengeMessages")
        google_messages.delete("messaging")
        google_messages.delete("Messaging")
        google_messages.delete("QKSMS")
        google_messages.delete("Mms")
        app_set_list.append(AppSet("GoogleMessages", [google_messages]))

        google_dialer = Package("GoogleDialer", "com.google.android.dialer", C.is_priv_app)
        google_dialer.predefined_file_list.append("framework/com.google.android.dialer.support.jar")
        google_dialer.delete("Dialer")
        app_set_list.append(AppSet("GoogleDialer", [google_dialer]))

        google_contacts = Package("GoogleContacts", "com.google.android.contacts", C.is_system_app)
        google_contacts.delete("Contacts")
        app_set_list.append(AppSet("GoogleContacts", [google_contacts]))

        carrier_services = Package("CarrierServices", "com.google.android.ims", C.is_priv_app)
        app_set_list.append(AppSet("CarrierServices", [carrier_services]))
        google_clock = Package("PrebuiltDeskClockGoogle", "com.google.android.deskclock", C.is_system_app,
                               "GoogleClock")
        google_clock.delete("DeskClock")
        google_clock.clean_flash_only = True
        app_set_list.append(AppSet("GoogleClock", [google_clock]))
        return app_set_list

    @staticmethod
    def get_omni_package():
        app_set_list = NikGappsPackages.get_basic_package()
        app_set_list.append(NikGappsPackages.get_setup_wizard())
        # Dropping pixelize support, need to keep it stock
        calculator = Package("CalculatorGooglePrebuilt", "com.google.android.calculator", C.is_system_app,
                             "GoogleCalculator")
        calculator.delete("ExactCalculator")
        calculator.delete("RevengeOSCalculator")
        app_set_list.append(AppSet("GoogleCalculator", [calculator]))
        google_drive = Package("Drive", "com.google.android.apps.docs", C.is_system_app)
        app_set_list.append(AppSet("Drive", [google_drive]))
        google_maps = Package("GoogleMaps", "com.google.android.apps.maps", C.is_priv_app)
        google_maps.delete("Maps")
        app_set_list.append(AppSet("GoogleMaps", [google_maps]))
        if TARGET_ANDROID_VERSION >= 11:
            google_location_history = Package("LocationHistoryPrebuilt", "com.google.android.gms.location.history",
                                              C.is_system_app, "GoogleLocationHistory")
            app_set_list.append(AppSet("GoogleLocationHistory", [google_location_history]))
        gmail = Package("PrebuiltGmail", "com.google.android.gm", C.is_system_app, "Gmail")
        gmail.delete("Email")
        gmail.delete("PrebuiltEmailGoogle")
        app_set_list.append(AppSet("Gmail", [gmail]))
        google_photos = Package("Photos", "com.google.android.apps.photos", C.is_system_app, "GooglePhotos")
        google_photos.delete("Gallery")
        google_photos.delete("SimpleGallery")
        google_photos.delete("Gallery2")
        google_photos.delete("MotGallery")
        google_photos.delete("MediaShortcuts")
        google_photos.delete("SimpleGallery")
        google_photos.delete("FineOSGallery")
        google_photos.delete("GalleryX")
        google_photos.delete("MiuiGallery")
        google_photos.delete("SnapdragonGallery")
        app_set_list.append(AppSet("GooglePhotos", [google_photos]))
        google_turbo = Package("Turbo", "com.google.android.apps.turbo", C.is_priv_app, "DeviceHealthServices")
        google_turbo.delete("TurboPrebuilt")
        app_set_list.append(AppSet("DeviceHealthServices", [google_turbo]))

        return app_set_list

    @staticmethod
    def get_stock_package():
        app_set_list = NikGappsPackages.get_omni_package()
        google_velvet = Package("Velvet", "com.google.android.googlequicksearchbox", C.is_priv_app)
        google_velvet.priv_app_permissions.append("android.permission.EXPAND_STATUS_BAR")
        google_velvet.priv_app_permissions.append("android.permission.SET_MEDIA_KEY_LISTENER")
        google_velvet.priv_app_permissions.append("android.permission.SET_VOLUME_KEY_LONG_PRESS_LISTENER")
        google_velvet.priv_app_permissions.append("android.permission.MANAGE_USB")
        google_velvet.priv_app_permissions.append("android.permission.START_ACTIVITIES_FROM_BACKGROUND")
        google_velvet.priv_app_permissions.append("android.permission.WRITE_APN_SETTINGS")
        google_velvet.priv_app_permissions.append("android.permission.BLUETOOTH_PRIVILEGED")
        google_velvet.clean_flash_only = True
        google_velvet.additional_installer_script = """
    set_prop "ro.opa.eligible_device" "true" "$install_partition/build.prop"
                        """
        google_assistant = Package("Assistant", "com.google.android.apps.googleassistant", C.is_priv_app)
        google_assistant.clean_flash_only = True
        app_set_list.append(AppSet("GoogleSearch", [google_velvet, google_assistant]))
        google_board = Package("LatinIMEGooglePrebuilt", "com.google.android.inputmethod.latin",
                               C.is_system_app, "GBoard")
        google_board.additional_installer_script = """
   set_prop "ro.com.google.ime.bs_theme" "true" "$install_partition/build.prop"
   set_prop "ro.com.google.ime.theme_id" "5" "$install_partition/build.prop"
   set_prop "ro.com.google.ime.system_lm_dir" "$install_partition/usr/share/ime/google/d3_lms" "$install_partition/build.prop"
        """
        google_board.delete("LatinIME")
        google_board.clean_flash_only = True
        app_set_list.append(AppSet("GBoard", [google_board]))
        app_set_list.append(AddonSet.get_pixel_launcher())
        if TARGET_ANDROID_VERSION >= 11:
            app_set_list.append(NikGappsPackages.get_google_files())
        google_recorder = Package("RecorderPrebuilt", "com.google.android.apps.recorder", C.is_priv_app,
                                  "GoogleRecorder")
        google_recorder.delete("Recorder")
        google_recorder.delete("QtiSoundRecorder")
        app_set_list.append(AppSet("GoogleRecorder", [google_recorder]))
        google_calendar = Package("CalendarGooglePrebuilt", "com.google.android.calendar", C.is_priv_app,
                                  "GoogleCalendar")
        google_calendar.delete("Calendar")
        google_calendar.delete("Etar")
        google_calendar.delete("SimpleCalendar")
        app_set_list.append(AppSet("GoogleCalendar", [google_calendar]))
        google_markup = Package("MarkupGoogle", "com.google.android.markup", C.is_system_app)
        app_set_list.append(AppSet("MarkupGoogle", [google_markup]))
        google_feedback = Package("GoogleFeedback", "com.google.android.feedback", C.is_priv_app,
                                  partition="system_ext")
        app_set_list.append(AppSet("GoogleFeedback", [google_feedback]))
        google_partner_setup = Package("PartnerSetupPrebuilt", "com.google.android.partnersetup", C.is_priv_app,
                                       "GooglePartnerSetup")
        app_set_list.append(AppSet("GooglePartnerSetup", [google_partner_setup]))
        google_sounds = Package("SoundPickerPrebuilt", "com.google.android.soundpicker", C.is_system_app,
                                "GoogleSounds")
        google_sounds.clean_flash_only = True
        app_set_list.append(AppSet("GoogleSounds", [google_sounds]))
        if TARGET_ANDROID_VERSION >= 10:
            android_device_policy = Package("DevicePolicyPrebuilt", "com.google.android.apps.work.clouddpc",
                                            C.is_system_app, "AndroidDevicePolicy")
            app_set_list.append(AppSet("AndroidDevicePolicy", [android_device_policy]))
        return app_set_list

    @staticmethod
    def get_full_package():
        app_set_list = NikGappsPackages.get_stock_package()
        google_keep = Package("PrebuiltKeep", "com.google.android.keep", C.is_priv_app, "GoogleKeep")
        app_set_list.append(AppSet("GoogleKeep", [google_keep]))
        google_play_books = Package("Books", "com.google.android.apps.books", C.is_system_app)
        app_set_list.append(AppSet("Books", [google_play_books]))
        youtube_music = Package("YouTubeMusicPrebuilt", "com.google.android.apps.youtube.music",
                                C.is_system_app,
                                "YouTubeMusic")
        youtube_music.delete("SnapdragonMusic")
        youtube_music.delete("GooglePlayMusic")
        youtube_music.delete("Eleven")
        app_set_list.append(AppSet("YouTubeMusic", [youtube_music]))
        play_games = Package("PlayGames", "com.google.android.play.games", C.is_system_app)
        app_set_list.append(AppSet("PlayGames", [play_games]))
        if TARGET_ANDROID_VERSION >= 10:
            google_device_setup = Package("OTAConfigPrebuilt", "com.google.android.apps.work.oobconfig",
                                          C.is_priv_app, "DeviceSetup")
            app_set_list.append(AppSet("DeviceSetup", [google_device_setup]))
        android_auto = Package("AndroidAutoStubPrebuilt", "com.google.android.projection.gearhead",
                               C.is_priv_app, "AndroidAuto")
        android_auto.clean_flash_only = True
        app_set_list.append(AppSet("AndroidAuto", [android_auto]))
        app_set_list.append(NikGappsPackages.get_chrome())
        return app_set_list

    @staticmethod
    def get_google_files():
        app_set_list = AppSet("GoogleFiles")
        google_files = Package("FilesPrebuilt", "com.google.android.apps.nbu.files", C.is_priv_app,
                               "GoogleFiles")
        app_set_list.add_package(google_files)
        storage_manager_google = Package("StorageManagerGoogle", "com.google.android.storagemanager",
                                         C.is_priv_app, "StorageManager", partition="system_ext")
        app_set_list.add_package(storage_manager_google)
        if TARGET_ANDROID_VERSION >= 11:
            documents_ui_google = Package("DocumentsUIGoogle", "com.google.android.documentsui", C.is_priv_app)
            documents_ui_google.delete("DocumentsUI")
            app_set_list.add_package(documents_ui_google)
        return app_set_list

    @staticmethod
    def get_chrome():
        google_chrome = Package("GoogleChrome", "com.android.chrome", C.is_system_app)
        google_chrome.delete("Bolt")
        google_chrome.delete("Browser")
        google_chrome.delete("Browser2")
        google_chrome.delete("BrowserIntl")
        google_chrome.delete("BrowserProviderProxy")
        google_chrome.delete("Chromium")
        google_chrome.delete("DuckDuckGo")
        google_chrome.delete("Fluxion")
        google_chrome.delete("Gello")
        google_chrome.delete("Jelly")
        google_chrome.delete("PA_Browser")
        google_chrome.delete("PABrowser")
        google_chrome.delete("YuBrowser")
        google_chrome.delete("BLUOpera")
        google_chrome.delete("BLUOperaPreinstall")
        google_chrome.delete("ViaBrowser")
        google_chrome.delete("Duckduckgo")
        app_set_list = AppSet("GoogleChrome")
        app_set_list.add_package(google_chrome)
        if TARGET_ANDROID_VERSION >= 10:
            google_webview = Package("WebViewGoogle", "com.google.android.webview", C.is_system_app)
            google_webview.delete("webview")
            trichromelibrary = Package("TrichromeLibrary", "com.google.android.trichromelibrary",
                                       C.is_system_app)
            app_set_list.add_package(google_webview)
            app_set_list.add_package(trichromelibrary)
        return app_set_list

    @staticmethod
    def get_setup_wizard():
        setup_wizard = Package("SetupWizardPrebuilt", "com.google.android.setupwizard", C.is_priv_app,
                               "SetupWizard")
        setup_wizard.delete("Provision")
        setup_wizard.delete("SetupWizard")
        setup_wizard.delete("LineageSetupWizard")
        setup_wizard.additional_installer_script = """
set_prop "setupwizard.feature.baseline_setupwizard_enabled" "true" "$install_partition/build.prop"
set_prop "ro.setupwizard.enterprise_mode" "1" "$install_partition/build.prop"
set_prop "ro.setupwizard.rotation_locked" "true" "$install_partition/build.prop"
set_prop "setupwizard.enable_assist_gesture_training" "true" "$install_partition/build.prop"
set_prop "setupwizard.theme" "glif_v3_light" "$install_partition/build.prop"
set_prop "setupwizard.feature.skip_button_use_mobile_data.carrier1839" "true" "$install_partition/build.prop"
set_prop "setupwizard.feature.show_pai_screen_in_main_flow.carrier1839" "false" "$install_partition/build.prop"
set_prop "setupwizard.feature.show_pixel_tos" "false" "$install_partition/build.prop"
        """
        google_restore = Package("GoogleRestore", "com.google.android.apps.restore", C.is_priv_app)
        android_migrate_prebuilt = Package("AndroidMigratePrebuilt", "com.google.android.apps.pixelmigrate",
                                           C.is_priv_app)
        setup_wizard_set = AppSet("SetupWizard")
        setup_wizard_set.add_package(setup_wizard)
        setup_wizard_set.add_package(google_restore)
        if TARGET_ANDROID_VERSION >= 10:
            google_one_time_initializer = Package("GoogleOneTimeInitializer", "com.google.android.onetimeinitializer",
                                                  C.is_priv_app, partition="system_ext")
            setup_wizard_set.add_package(google_one_time_initializer)
        if TARGET_ANDROID_VERSION < 12:
            setup_wizard_set.add_package(android_migrate_prebuilt)
        return setup_wizard_set

    @staticmethod
    def get_pixelize_set():
        pixel_setup_wizard_overlay = Package("PixelSetupWizardOverlay", "com.google.android.pixel.setupwizard.overlay",
                                             C.is_system_app)
        pixel_setup_wizard_aod_overlay = Package("PixelSetupWizardAodOverlay",
                                                 "com.google.android.pixel.setupwizard.overlay.aod",
                                                 C.is_system_app)
        pixel_setup_wizard = Package("PixelSetupWizard", "com.google.android.pixel.setupwizard", C.is_priv_app,
                                     partition="system_ext")
        android_migrate_prebuilt = Package("AndroidMigratePrebuilt", "com.google.android.apps.pixelmigrate",
                                           C.is_priv_app)
        pixel_tips = Package("TipsPrebuilt", "com.google.android.apps.tips", C.is_priv_app, "PixelTips")
        pixel_config_overlays = Package("PixelConfigOverlays", None, None)
        pixel_config_overlays.predefined_file_list.append(
            "overlay/IconPackRoundedPixelLauncher/IconPackRoundedPixelLauncherOverlay.apk")
        pixel_config_overlays.predefined_file_list.append(
            "overlay/IconPackFilledPixelLauncher/IconPackFilledPixelLauncherOverlay.apk")
        pixel_config_overlays.predefined_file_list.append(
            "overlay/IconPackCircularPixelLauncher/IconPackCircularPixelLauncherOverlay.apk")
        pixel_config_overlays.predefined_file_list.append("overlay/PixelConfigOverlay2018.apk")
        pixel_config_overlays.predefined_file_list.append("overlay/PixelConfigOverlay2019.apk")
        pixel_config_overlays.predefined_file_list.append("overlay/PixelConfigOverlay2019Midyear.apk")
        pixel_config_overlays.predefined_file_list.append("overlay/PixelConfigOverlaySunfish.apk")
        pixelize_set = AppSet("Pixelize")
        if TARGET_ANDROID_VERSION == 10:
            pixelize_set.add_package(pixel_setup_wizard_overlay)
            pixelize_set.add_package(pixel_setup_wizard_aod_overlay)
        if TARGET_ANDROID_VERSION in (10, 11):
            pixelize_set.add_package(pixel_setup_wizard)
            pixelize_set.add_package(android_migrate_prebuilt)
            pixelize_set.add_package(pixel_tips)
        if TARGET_ANDROID_VERSION == 11:
            pixelize_set.add_package(pixel_config_overlays)
        return pixelize_set

    @staticmethod
    def get_lawnchair():
        lawnchair_set = AppSet("Lawnchair")
        from Config import TARGET_ANDROID_VERSION
        if TARGET_ANDROID_VERSION == 10:
            lawnchair_ci = Package("Lawnchair", "ch.deletescape.lawnchair.ci", C.is_priv_app)
            if "etc/permissions/privapp-permissions-lawnchair.xml" not in lawnchair_ci.predefined_file_list:
                lawnchair_ci.predefined_file_list.append("etc/permissions/privapp-permissions-lawnchair.xml")
            if "etc/sysconfig/lawnchair-hiddenapi-package-whitelist.xml" not in lawnchair_ci.predefined_file_list:
                lawnchair_ci.predefined_file_list.append("etc/sysconfig/lawnchair-hiddenapi-package-whitelist.xml")
            overlay = "overlay/LawnchairRecentsProvider/LawnchairRecentsProvider.apk"
            lawnchair_recents_provider = Package("LawnchairRecentsProvider", "com.android.overlay.shady.recents", None)
            if overlay not in lawnchair_recents_provider.predefined_file_list:
                lawnchair_recents_provider.predefined_file_list.append(overlay)
            lawnchair_set.add_package(lawnchair_ci)
            lawnchair_recents_provider.enabled = 0
            lawnchair_set.add_package(lawnchair_recents_provider)
        else:
            lawnchair = Package("Lawnchair", "ch.deletescape.lawnchair.plah", C.is_priv_app)
            lawnchair_set.add_package(lawnchair)
        lawnfeed = Package("Lawnfeed", "ch.deletescape.lawnchair.lawnfeed", C.is_system_app)
        lawnchair_set.add_package(lawnfeed)
        return lawnchair_set
