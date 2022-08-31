from .Package import Package
from .Constants import Constants
from .AppSet import AppSet
from Config import TARGET_ANDROID_VERSION


class AddonSet:

    @staticmethod
    def get_addon_packages(addon_name=None):
        addon_set_list = [
            AddonSet.get_pixel_live_wallpapers(),
            AddonSet.get_google_fi(),
            AddonSet.get_google_duo(),
            AddonSet.get_google_docs(),
            AddonSet.get_google_slides(),
            AddonSet.get_google_sheets(),
            AddonSet.get_youtube(),
            AddonSet.get_google_tts(),
            AddonSet.get_pixel_setup_wizard(),
            AddonSet.get_google_talkback(),
            AddonSet.get_pixel_launcher()
        ]
        # if TARGET_ANDROID_VERSION in (10, 11):
        #     addon_set_list.append(AddonSet.get_pixel_setup_wizard())
        if TARGET_ANDROID_VERSION >= 11:
            addon_set_list.append(AddonSet.get_flipendo())
        if addon_name is None:
            return addon_set_list
        else:
            for addon_set in addon_set_list:
                if addon_set.title == addon_name:
                    return [addon_set]
        return None

    @staticmethod
    def get_vanced_manager():
        vanced_manager = Package("VancedManager", "com.vanced.manager", Constants.is_system_app)
        return AppSet("VancedManager", [vanced_manager])

    @staticmethod
    def get_google_camera_go():
        google_camera_lite = Package("GoogleCameraGo", "com.google.android.apps.cameralite", Constants.is_system_app)
        return AppSet("GoogleCameraGo", [google_camera_lite])

    @staticmethod
    def get_lineageos_recorder():
        los_recorder = Package("Recorder", "org.lineageos.recorder", Constants.is_system_app)
        return AppSet("Recorder", [los_recorder])

    @staticmethod
    def get_google_tts():
        google_tts = Package("GoogleTTS", "com.google.android.tts", Constants.is_system_app)
        google_tts.delete("PicoTts")
        return AppSet("GoogleTTS", [google_tts])

    @staticmethod
    def get_google_talkback():
        talkback = Package("talkback", "com.google.android.marvin.talkback", Constants.is_system_app, "GoogleTalkback")
        return AppSet("GoogleTalkback", [talkback])

    @staticmethod
    def get_snap_camera():
        snap = Package("Snap", "org.lineageos.snap", Constants.is_priv_app)
        snap.delete("GoogleCameraGo")
        snap.delete("ScreenRecorder")
        return AppSet("Snap", [snap])

    @staticmethod
    def get_flipendo():
        flipendo = Package("Flipendo", "com.google.android.flipendo", Constants.is_system_app)
        return AppSet("Flipendo", [flipendo])

    @staticmethod
    def get_google_docs():
        google_docs = Package("GoogleDocs", "com.google.android.apps.docs.editors.docs", Constants.is_system_app)
        return AppSet("GoogleDocs", [google_docs])

    @staticmethod
    def get_google_sheets():
        google_sheets = Package("GoogleSheets", "com.google.android.apps.docs.editors.sheets", Constants.is_system_app)
        return AppSet("GoogleSheets", [google_sheets])

    @staticmethod
    def get_google_slides():
        google_slides = Package("GoogleSlides", "com.google.android.apps.docs.editors.slides", Constants.is_system_app)
        return AppSet("GoogleSlides", [google_slides])

    @staticmethod
    def get_google_duo():
        google_duo = Package("GoogleDuo", "com.google.android.apps.tachyon", Constants.is_system_app)
        return AppSet("GoogleDuo", [google_duo])

    @staticmethod
    def get_device_personalization_services():
        device_personalization_services = Package("MatchmakerPrebuiltPixel4", "com.google.android.as",
                                                  Constants.is_priv_app, "DevicePersonalizationServices")
        gapps_list = []
        if TARGET_ANDROID_VERSION >= 10:
            if TARGET_ANDROID_VERSION == 10:
                device_personalization_services.predefined_file_list.append(
                    "overlay/DevicePersonalizationServicesConfig.apk")
            device_personalization_services.delete("DevicePersonalizationPrebuiltPixel4")
            gapps_list.append(device_personalization_services)
        return AppSet("DevicePersonalizationServices", gapps_list)

    @staticmethod
    def get_google_fi():
        google_fi_set = AppSet("GoogleFi")
        if TARGET_ANDROID_VERSION == 11:
            google_fi = Package("Tycho", "com.google.android.apps.tycho", Constants.is_system_app)
            google_fi_set.add_package(google_fi)
            gcs = Package("GCS", "com.google.android.apps.gcs", Constants.is_priv_app)
            google_fi_set.add_package(gcs)
        return google_fi_set

    @staticmethod
    def get_pixel_launcher():
        pixel_launcher = Package("NexusLauncherPrebuilt", "com.google.android.apps.nexuslauncher",
                                 Constants.is_priv_app, "PixelLauncher", partition="system_ext")
        pixel_launcher.priv_app_permissions.append("android.permission.PACKAGE_USAGE_STATS")
        # pixel_launcher.delete("TrebuchetQuickStep")
        device_personalization_services = Package("MatchmakerPrebuiltPixel4", "com.google.android.as",
                                                  Constants.is_priv_app, "DevicePersonalizationServices")
        gapps_list = [pixel_launcher]
        if TARGET_ANDROID_VERSION >= 9:
            device_personalization_services.delete("DevicePersonalizationPrebuiltPixel4")
            gapps_list.append(device_personalization_services)
        if TARGET_ANDROID_VERSION >= 11:
            quick_access_wallet = Package("QuickAccessWallet", "com.android.systemui.plugin.globalactions.wallet",
                                          Constants.is_priv_app)
            gapps_list.append(quick_access_wallet)
        google_wallpaper = Package("WallpaperPickerGooglePrebuilt", "com.google.android.apps.wallpaper",
                                   Constants.is_priv_app, "GoogleWallpaper", partition="system_ext")
        gapps_list.append(google_wallpaper)
        return AppSet("PixelLauncher", gapps_list)

    @staticmethod
    def get_mixplorer():
        mixplorer_silver = Package("MixPlorerSilver", "com.mixplorer.silver", Constants.is_system_app,
                                   "MixPlorerSilver")
        mixplorer_silver.delete("MixPlorer")
        return AppSet("MixPlorerSilver", [mixplorer_silver])

    @staticmethod
    def get_adaway():
        adaway = Package("AdAway", "org.adaway", Constants.is_system_app)
        return AppSet("AdAway", [adaway])

    @staticmethod
    def get_lawnchair():
        lawnchair_set = AppSet("Lawnchair")
        from Config import TARGET_ANDROID_VERSION
        if TARGET_ANDROID_VERSION == 9:
            lawnchair = Package("Lawnchair", "ch.deletescape.lawnchair.plah", Constants.is_priv_app)
            lawnchair_set.add_package(lawnchair)
        if TARGET_ANDROID_VERSION == 10:
            lawnchair_ci = Package("Lawnchair", "ch.deletescape.lawnchair.ci", Constants.is_priv_app)
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
        if TARGET_ANDROID_VERSION == 11:
            return [None]
        lawnfeed = Package("Lawnfeed", "ch.deletescape.lawnchair.lawnfeed", Constants.is_system_app)
        lawnchair_set.add_package(lawnfeed)
        return lawnchair_set

    @staticmethod
    def get_pixel_live_wallpapers():
        wallpapers_breel_2019 = Package("WallpapersBReel2019", "com.breel.wallpapers19", Constants.is_system_app)
        wallpapers_breel_2020a = Package("WallpapersBReel2020a", "com.breel.wallpapers20a", Constants.is_system_app)
        pixel_live_wallpaper = Package("PixelLiveWallpaperPrebuilt", "com.google.pixel.livewallpaper",
                                       Constants.is_priv_app, "PixelLiveWallpaper")
        wallpapers_breel_2020 = Package("WallpapersBReel2020", "com.breel.wallpapers20", Constants.is_system_app)
        pixel_live_wallpaper_set = AppSet("PixelLiveWallpapers")
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2019)
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2020a)
        pixel_live_wallpaper_set.add_package(pixel_live_wallpaper)
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2020)
        if TARGET_ANDROID_VERSION >= 12:
            pixel_wallpapers_2021 = Package("PixelWallpapers2021", "com.google.android.apps.wallpaper.pixel",
                                            Constants.is_system_app)
            micropaper = Package("MicropaperPrebuilt", "com.google.pixel.dynamicwallpapers", Constants.is_system_app,
                                 "Micropaper")
            pixel_live_wallpaper_set.add_package(pixel_wallpapers_2021)
            pixel_live_wallpaper_set.add_package(micropaper)
        return pixel_live_wallpaper_set

    @staticmethod
    def get_poke_pix_live_wallpapers():
        wallpapers_breel_2019 = Package("WallpapersBReel2019", "com.breel.wallpapers19", Constants.is_system_app)
        wallpapers_breel_2020a = Package("WallpapersBReel2020a", "com.breel.wallpapers20a", Constants.is_system_app)
        pixel_live_wallpaper = Package("PixelLiveWallpaperPrebuilt", "com.google.pixel.livewallpaper",
                                       Constants.is_priv_app, "PixelLiveWallpaper")
        wallpapers_breel_2020 = Package("WallpapersBReel2020", "com.breel.wallpapers20", Constants.is_system_app)
        pixel_live_wallpaper_set = AppSet("PokePixLiveWallpapers")
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2019)
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2020a)
        pixel_live_wallpaper_set.add_package(pixel_live_wallpaper)
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2020)
        return pixel_live_wallpaper_set

    @staticmethod
    def get_youtube():
        youtube = Package("YouTube", "com.google.android.youtube", Constants.is_system_app)
        return AppSet("YouTube", [youtube])

    @staticmethod
    def get_youtube_black():
        youtube_vanced_black = Package("YouTube", "com.vanced.android.youtube", Constants.is_system_app,
                                       "YouTubeVancedBlack")
        vanced_gms = Package("VancedGms", "com.mgoogle.android.gms", Constants.is_system_app)
        return AppSet("YouTubeVancedBlack", [youtube_vanced_black, vanced_gms])

    @staticmethod
    def get_youtube_dark():
        youtube_vanced_dark = Package("YouTube", "com.vanced.android.youtube", Constants.is_system_app,
                                      "YouTubeVancedDark")
        vanced_gms = Package("VancedGms", "com.mgoogle.android.gms", Constants.is_system_app)
        return AppSet("YouTubeVancedDark", [youtube_vanced_dark, vanced_gms])

    @staticmethod
    def get_youtube_music():
        youtube_music = Package("YMusic", "com.vanced.android.apps.youtube.music", Constants.is_system_app,
                                "YouTubeVancedMusic")
        youtube_music.delete("GooglePlayMusic")
        youtube_music.delete("SnapdragonMusic")
        youtube_music.delete("YouTubeMusicPrebuilt")
        youtube_music.delete("Eleven")
        vanced_gms = Package("VancedGms", "com.mgoogle.android.gms", Constants.is_system_app)
        return AppSet("YouTubeVancedMusic", [youtube_music, vanced_gms])

    @staticmethod
    def get_pixel_setup_wizard():
        setup_wizard = Package("SetupWizardPrebuilt", "com.google.android.setupwizard", Constants.is_priv_app,
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
        google_restore = Package("GoogleRestore", "com.google.android.apps.restore", Constants.is_priv_app)
        pixel_setup_wizard_overlay = Package("PixelSetupWizardOverlay", "com.google.android.pixel.setupwizard.overlay",
                                             Constants.is_system_app)
        pixel_setup_wizard_aod_overlay = Package("PixelSetupWizardAodOverlay",
                                                 "com.google.android.pixel.setupwizard.overlay.aod",
                                                 Constants.is_system_app)
        pixel_setup_wizard = Package("PixelSetupWizard", "com.google.android.pixel.setupwizard", Constants.is_priv_app,
                                     partition="system_ext")
        pixel_setup_wizard.delete("LineageSetupWizard")
        android_migrate_prebuilt = Package("AndroidMigratePrebuilt", "com.google.android.apps.pixelmigrate",
                                           Constants.is_priv_app)
        pixel_tips = Package("TipsPrebuilt", "com.google.android.apps.tips", Constants.is_priv_app, "PixelTips")
        pixel_config_overlays = Package("PixelConfigOverlays", None, None)
        pixel_config_overlays.predefined_file_list.append("overlay/PixelConfigOverlay2018.apk")
        pixel_config_overlays.predefined_file_list.append("overlay/PixelConfigOverlay2019.apk")
        pixel_config_overlays.predefined_file_list.append("overlay/PixelConfigOverlay2019Midyear.apk")
        pixel_config_overlays.predefined_file_list.append("overlay/PixelConfigOverlaySunfish.apk")

        setup_wizard_set = AppSet("PixelSetupWizard")
        setup_wizard_set.add_package(setup_wizard)
        setup_wizard_set.add_package(google_restore)
        if TARGET_ANDROID_VERSION >= 10:
            google_one_time_initializer = Package("GoogleOneTimeInitializer", "com.google.android.onetimeinitializer",
                                                  Constants.is_priv_app, partition="system_ext")
            setup_wizard_set.add_package(google_one_time_initializer)
        if TARGET_ANDROID_VERSION == 10:
            setup_wizard_set.add_package(pixel_setup_wizard_overlay)
            setup_wizard_set.add_package(pixel_setup_wizard_aod_overlay)
        if TARGET_ANDROID_VERSION >= 10:
            setup_wizard_set.add_package(pixel_setup_wizard)
            if TARGET_ANDROID_VERSION < 12:
                setup_wizard_set.add_package(android_migrate_prebuilt)
            # setup_wizard_set.add_package(pixel_tips)
        # if TARGET_ANDROID_VERSION == 11:
        # setup_wizard_set.add_package(pixel_config_overlays)
        return setup_wizard_set

    @staticmethod
    def get_documents_ui():
        documents_ui = Package("DocumentsUI", "com.android.documentsui", Constants.is_priv_app)
        return AppSet("DocumentsUI", [documents_ui])
