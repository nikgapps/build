import Config
from .Package import Package
from .C import C
from .AppSet import AppSet


class AddonSet:

    @staticmethod
    def get_addon_packages(addon_name=None):
        addon_set_list = [
            AddonSet.get_google_fi(),
            AddonSet.get_google_duo(),
            AddonSet.get_google_docs(),
            AddonSet.get_google_slides(),
            AddonSet.get_google_sheets(),
            AddonSet.get_youtube(),
            AddonSet.get_google_tts(),
            AddonSet.get_pixel_setup_wizard(),
            AddonSet.get_google_talkback()
        ]
        if float(Config.TARGET_ANDROID_VERSION) == float(12.1):
            addon_set_list.append(AddonSet.get_lawnchair())
        # if TARGET_ANDROID_VERSION in (10, 11):
        #     addon_set_list.append(AddonSet.get_pixel_setup_wizard())
        if float(Config.TARGET_ANDROID_VERSION) >= 11:
            addon_set_list.append(AddonSet.get_flipendo())
        if float(Config.TARGET_ANDROID_VERSION) < 13:
            addon_set_list.append(AddonSet.get_pixel_live_wallpapers())
        if addon_name is None:
            return addon_set_list
        else:
            for addon_set in addon_set_list:
                if addon_set.title == addon_name:
                    return [addon_set]
        return None

    @staticmethod
    def get_google_camera_go():
        google_camera_lite = Package("GoogleCameraGo", "com.google.android.apps.cameralite", C.is_system_app)
        return AppSet("GoogleCameraGo", [google_camera_lite])

    @staticmethod
    def get_lineageos_recorder():
        los_recorder = Package("Recorder", "org.lineageos.recorder", C.is_system_app)
        return AppSet("Recorder", [los_recorder])

    @staticmethod
    def get_google_tts():
        google_tts = Package("GoogleTTS", "com.google.android.tts", C.is_system_app)
        google_tts.delete("PicoTts")
        return AppSet("GoogleTTS", [google_tts])

    @staticmethod
    def get_google_talkback():
        talkback = Package("talkback", "com.google.android.marvin.talkback", C.is_system_app, "GoogleTalkback")
        return AppSet("GoogleTalkback", [talkback])

    @staticmethod
    def get_snap_camera():
        snap = Package("Snap", "org.lineageos.snap", C.is_priv_app)
        snap.delete("GoogleCameraGo")
        snap.delete("ScreenRecorder")
        return AppSet("Snap", [snap])

    @staticmethod
    def get_flipendo():
        flipendo = Package("Flipendo", "com.google.android.flipendo", C.is_system_app)
        return AppSet("Flipendo", [flipendo])

    @staticmethod
    def get_google_docs():
        google_docs = Package("GoogleDocs", "com.google.android.apps.docs.editors.docs", C.is_system_app)
        return AppSet("GoogleDocs", [google_docs])

    @staticmethod
    def get_google_sheets():
        google_sheets = Package("GoogleSheets", "com.google.android.apps.docs.editors.sheets", C.is_system_app)
        return AppSet("GoogleSheets", [google_sheets])

    @staticmethod
    def get_google_slides():
        google_slides = Package("GoogleSlides", "com.google.android.apps.docs.editors.slides", C.is_system_app)
        return AppSet("GoogleSlides", [google_slides])

    @staticmethod
    def get_google_duo():
        google_duo = Package("GoogleDuo", "com.google.android.apps.tachyon", C.is_system_app)
        return AppSet("GoogleDuo", [google_duo])

    @staticmethod
    def get_device_personalization_services():
        device_personalization_services = Package("MatchmakerPrebuiltPixel4", "com.google.android.as",
                                                  C.is_priv_app, "DevicePersonalizationServices")
        gapps_list = []
        device_personalization_services.delete("DevicePersonalizationPrebuiltPixel4")
        gapps_list.append(device_personalization_services)
        return AppSet("DevicePersonalizationServices", gapps_list)

    @staticmethod
    def get_google_fi():
        google_fi_set = AppSet("GoogleFi")
        if float(Config.TARGET_ANDROID_VERSION) == 11:
            google_fi = Package("Tycho", "com.google.android.apps.tycho", C.is_system_app)
            google_fi_set.add_package(google_fi)
            gcs = Package("GCS", "com.google.android.apps.gcs", C.is_priv_app)
            google_fi_set.add_package(gcs)
        return google_fi_set

    @staticmethod
    def get_pixel_launcher():
        pixel_launcher = Package("NexusLauncherPrebuilt", "com.google.android.apps.nexuslauncher",
                                 C.is_priv_app, "PixelLauncher", partition="system_ext")
        pixel_launcher.priv_app_permissions.append("android.permission.PACKAGE_USAGE_STATS")
        pixel_launcher.delete("TrebuchetQuickStep")
        pixel_launcher.delete("Lawnchair")
        pixel_launcher.delete_overlay("Lawnchair")
        pixel_launcher.validation_script = """
skip_validation_check=$(ReadConfigValue "skip_validation_check" "$nikgapps_config_file_name")
[ -z "$skip_validation_check" ] && skip_validation_check=0
addToLog "- Skip validation check: $skip_validation_check"
if [ "$skip_validation_check" = "0" ]; then
    crdroid_version=$(ReadConfigValue "ro.crdroid.version" "/system/build.prop")
    addToLog "- CrDroid version: $crdroid_version"
    if [ -n "$crdroid_version" ] && [ "$crdroid_version" = "13.0" ]; then
        ui_print "- Skipping Pixel Launcher as it is not compatible with CrDroid for now"
    else
        find_install_mode
    fi
else
    find_install_mode
fi
        """
        device_personalization_services = Package("MatchmakerPrebuiltPixel4", "com.google.android.as",
                                                  C.is_priv_app, "DevicePersonalizationServices")
        gapps_list = [pixel_launcher]
        if float(Config.TARGET_ANDROID_VERSION) >= 9:
            device_personalization_services.delete("DevicePersonalizationPrebuiltPixel4")
            gapps_list.append(device_personalization_services)
        if float(Config.TARGET_ANDROID_VERSION) >= 11:
            quick_access_wallet = Package("QuickAccessWallet", "com.android.systemui.plugin.globalactions.wallet",
                                          C.is_priv_app)
            gapps_list.append(quick_access_wallet)
        google_wallpaper = Package("WallpaperPickerGooglePrebuilt", "com.google.android.apps.wallpaper",
                                   C.is_priv_app, "GoogleWallpaper", partition="system_ext")
        gapps_list.append(google_wallpaper)
        return AppSet("PixelLauncher", gapps_list)

    @staticmethod
    def get_google_wallpaper():
        google_wallpaper = Package("WallpaperPickerGooglePrebuilt", "com.google.android.apps.wallpaper",
                                   C.is_priv_app, "GoogleWallpaper", partition="system_ext")
        return AppSet("GoogleWallpaper", [google_wallpaper])

    @staticmethod
    def get_mixplorer():
        mixplorer_silver = Package("MixPlorerSilver", "com.mixplorer.silver", C.is_system_app,
                                   "MixPlorerSilver")
        mixplorer_silver.delete("MixPlorer")
        return AppSet("MixPlorerSilver", [mixplorer_silver])

    @staticmethod
    def get_adaway():
        adaway = Package("AdAway", "org.adaway", C.is_system_app)
        return AppSet("AdAway", [adaway])

    @staticmethod
    def get_lawnchair():
        lawnchair = Package("Lawnchair", "app.lawnchair", C.is_system_app)
        lawnchair.delete_overlay("PixelLauncher")
        lawnchair.delete("NexusLauncherPrebuilt")
        lawnchair.delete("NexusLauncherRelease")
        return AppSet("Lawnchair", [lawnchair])

    @staticmethod
    def get_pixel_live_wallpapers():
        wallpapers_breel_2019 = Package("WallpapersBReel2019", "com.breel.wallpapers19", C.is_system_app)
        wallpapers_breel_2020a = Package("WallpapersBReel2020a", "com.breel.wallpapers20a", C.is_system_app)
        pixel_live_wallpaper = Package("PixelLiveWallpaperPrebuilt", "com.google.pixel.livewallpaper",
                                       C.is_priv_app, "PixelLiveWallpaper")
        wallpapers_breel_2020 = Package("WallpapersBReel2020", "com.breel.wallpapers20", C.is_system_app)
        pixel_live_wallpaper_set = AppSet("PixelLiveWallpapers")
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2019)
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2020a)
        pixel_live_wallpaper_set.add_package(pixel_live_wallpaper)
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2020)
        if float(Config.TARGET_ANDROID_VERSION) >= 12:
            pixel_wallpapers_2021 = Package("PixelWallpapers2021", "com.google.android.apps.wallpaper.pixel",
                                            C.is_system_app)
            micropaper = Package("MicropaperPrebuilt", "com.google.pixel.dynamicwallpapers", C.is_system_app,
                                 "Micropaper")
            pixel_live_wallpaper_set.add_package(pixel_wallpapers_2021)
            pixel_live_wallpaper_set.add_package(micropaper)
        return pixel_live_wallpaper_set

    @staticmethod
    def get_poke_pix_live_wallpapers():
        wallpapers_breel_2019 = Package("WallpapersBReel2019", "com.breel.wallpapers19", C.is_system_app)
        wallpapers_breel_2020a = Package("WallpapersBReel2020a", "com.breel.wallpapers20a", C.is_system_app)
        pixel_live_wallpaper = Package("PixelLiveWallpaperPrebuilt", "com.google.pixel.livewallpaper",
                                       C.is_priv_app, "PixelLiveWallpaper")
        wallpapers_breel_2020 = Package("WallpapersBReel2020", "com.breel.wallpapers20", C.is_system_app)
        pixel_live_wallpaper_set = AppSet("PokePixLiveWallpapers")
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2019)
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2020a)
        pixel_live_wallpaper_set.add_package(pixel_live_wallpaper)
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2020)
        return pixel_live_wallpaper_set

    @staticmethod
    def get_youtube():
        youtube = Package("YouTube", "com.google.android.youtube", C.is_system_app)
        return AppSet("YouTube", [youtube])

    @staticmethod
    def get_pixel_setup_wizard():
        setup_wizard = Package("SetupWizardPrebuilt", "com.google.android.setupwizard", C.is_priv_app,
                               "SetupWizard")
        setup_wizard.delete("Provision")
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
        pixel_setup_wizard_overlay = Package("PixelSetupWizardOverlay", "com.google.android.pixel.setupwizard.overlay",
                                             C.is_system_app)
        pixel_setup_wizard_aod_overlay = Package("PixelSetupWizardAodOverlay",
                                                 "com.google.android.pixel.setupwizard.overlay.aod",
                                                 C.is_system_app)
        pixel_setup_wizard = Package("PixelSetupWizard", "com.google.android.pixel.setupwizard", C.is_priv_app,
                                     partition="system_ext")
        pixel_setup_wizard.delete("LineageSetupWizard")
        android_migrate_prebuilt = Package("AndroidMigratePrebuilt", "com.google.android.apps.pixelmigrate",
                                           C.is_priv_app)
        pixel_tips = Package("TipsPrebuilt", "com.google.android.apps.tips", C.is_priv_app, "PixelTips")
        pixel_config_overlays = Package("PixelConfigOverlays", None, None)
        pixel_config_overlays.predefined_file_list.append("overlay/PixelConfigOverlay2018.apk")
        pixel_config_overlays.predefined_file_list.append("overlay/PixelConfigOverlay2019.apk")
        pixel_config_overlays.predefined_file_list.append("overlay/PixelConfigOverlay2019Midyear.apk")
        pixel_config_overlays.predefined_file_list.append("overlay/PixelConfigOverlaySunfish.apk")

        setup_wizard_set = AppSet("PixelSetupWizard")
        setup_wizard_set.add_package(setup_wizard)
        setup_wizard_set.add_package(google_restore)
        if float(Config.TARGET_ANDROID_VERSION) >= 10:
            google_one_time_initializer = Package("GoogleOneTimeInitializer", "com.google.android.onetimeinitializer",
                                                  C.is_priv_app, partition="system_ext")
            setup_wizard_set.add_package(google_one_time_initializer)
        if float(Config.TARGET_ANDROID_VERSION) == 10:
            setup_wizard_set.add_package(pixel_setup_wizard_overlay)
            setup_wizard_set.add_package(pixel_setup_wizard_aod_overlay)
        if float(Config.TARGET_ANDROID_VERSION) >= 10:
            setup_wizard_set.add_package(pixel_setup_wizard)
            if float(Config.TARGET_ANDROID_VERSION) < 12:
                setup_wizard_set.add_package(android_migrate_prebuilt)
            # setup_wizard_set.add_package(pixel_tips)
        # if TARGET_ANDROID_VERSION == 11:
        # setup_wizard_set.add_package(pixel_config_overlays)
        return setup_wizard_set

    @staticmethod
    def get_documents_ui():
        documents_ui = Package("DocumentsUI", "com.android.documentsui", C.is_priv_app)
        return AppSet("DocumentsUI", [documents_ui])
