
from bs4 import BeautifulSoup

from NikGapps.Web.Requests import Requests


class ApkMirror:

    def __init__(self, android_version):
        self.android_version = str(android_version)
        self.oem = "apk_mirror"
        self.oem = self.oem.lower()
        self.tracker = self.oem
        self.host = "https://www.apkmirror.com"
        self.regex = '^https?://www.apkmirror.com/apk/[^/]+/[^/]+'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        # apk mirror names can be dynamically fetched from tracker too, putting it here for now
        self.allApkMirrorNames = {
            'com.android.chrome': 'chrome',
            'com.android.facelock': 'trusted-face',
            'com.android.vending': 'google-play-store',
            'com.android.vending.leanback': 'google-play-store-android-tv',
            'com.google.android.apps.books': 'google-play-books',
            'com.google.android.apps.cloudprint': 'cloud-print',
            'com.google.android.apps.docs': 'drive',
            'com.google.android.apps.docs.editors.docs': 'docs',
            'com.google.android.apps.docs.editors.sheets': 'sheets',
            'com.google.android.apps.docs.editors.slides': 'slides',
            'com.google.android.apps.enterprise.dmagent': 'device-policy',
            'com.google.android.apps.fitness': 'fit',
            'com.google.android.apps.gcs': 'google-connectivity-services',
            'com.google.android.apps.inputmethod.hindi': 'google-indic-keyboard',
            'com.google.android.apps.inputmethod.zhuyin': 'google-zhuyin-input',
            'com.google.android.apps.magazines': 'google-news',
            'com.google.android.apps.maps': 'maps',
            'com.google.android.apps.mediashell': 'chromecast-built-in',
            'com.google.android.apps.messaging': 'messenger-google-inc',
            'com.google.android.apps.nexuslauncher': 'pixel-launcher',
            'com.google.android.apps.photos': 'photos',
            'com.google.android.apps.photos.vrmode': 'google-photos-daydream',
            'com.google.android.apps.pixelmigrate': 'data-transfer-tool',
            'com.google.android.apps.restore': 'android-setup',
            'com.google.android.apps.translate': 'translate',
            'com.google.android.apps.tachyon': 'duo-by-google',
            'com.google.android.apps.turbo': 'device-health-services',
            'com.google.android.apps.tv.launcherx': 'google-tv-home-android-tv',
            'com.google.android.apps.tycho': 'project-fi',
            'com.google.android.apps.walletnfcrel': 'google-pay',
            'com.google.android.apps.wallpaper': 'google-wallpaper-picker',
            'com.google.android.as': 'device-personalization-services',
            'com.google.android.backdrop': 'backdrop-daydream-android-tv',
            'com.google.android.backuptransport': 'google-backup-transport',
            'com.google.android.calculator': 'google-calculator',
            'com.google.android.calendar': 'calendar',
            'com.google.android.configupdater': 'configupdater',
            'com.google.android.contacts': 'google-contacts',
            'com.google.android.deskclock': 'clock',
            'com.google.android.dialer': 'google-phone',
            'com.google.android.ears': 'sound-search-for-google-play',
            'com.google.android.gm': 'gmail',
            'com.google.android.gm.exchange': 'exchange-services',
            'com.google.android.gms': 'google-play-services',
            'com.google.android.gms.leanback': 'google-play-services-android-tv',
            'com.google.android.googlecamera': 'camera',
            'com.google.android.googlequicksearchbox': 'google-search',
            'com.google.android.gsf': 'google-services-framework',
            'com.google.android.gsf.login': 'google-account-manager',
            'com.google.android.ims': 'carrier-services-2',
            'com.google.android.inputmethod.japanese': 'google-japanese-input',
            'com.google.android.inputmethod.korean': 'google-korean-input',
            'com.google.android.inputmethod.latin': 'gboard',
            'com.google.android.inputmethod.pinyin': 'google-pinyin-input',
            'com.google.android.instantapps.supervisor': 'google-play-services-for-instant-apps',
            'com.google.android.katniss': 'google-app-for-android-tv-android-tv',
            'com.google.android.keep': 'keep',
            'com.google.android.launcher': 'google-now-launcher',
            'com.google.android.leanbacklauncher': 'android-tv-launcher-android-tv',
            'com.google.android.marvin.talkback': 'android-accessibility-suite',
            'com.google.android.marvin.talkback.leanback': 'android-accessibility-suite-android-tv',
            'com.google.android.music': 'google-play-music',
            'com.google.android.nexusicons': 'pixel-launcher-icons',
            'com.google.android.onetimeinitializer': 'google-one-time-init',
            'com.google.android.partnersetup': 'google-partner-setup',
            'com.google.android.play.games': 'google-play-games',
            'com.google.android.play.games.leanback': 'google-play-games-android-tv',
            'com.google.android.projection.gearhead': 'android-auto',
            'com.google.android.settings.intelligence': 'settings-suggestions',
            'com.google.android.setupwizard': 'setup-wizard',
            'com.google.android.soundpicker': 'sounds',
            'com.google.android.storagemanager': 'storage-manager',
            'com.google.android.street': 'street-view',
            'com.google.android.syncadapters.contacts': 'google-contacts-sync',
            'com.google.android.tag': 'tags-google',
            'com.google.android.talk': 'hangouts',
            'com.google.android.trichromelibrary': 'trichrome-library',
            'com.google.android.tts': 'google-text-to-speech-engine',
            'com.google.android.tv': 'live-channels-android-tv',
            'com.google.android.tv.remote': 'remote-control',
            'com.google.android.tvlauncher': 'android-tv-home-android-tv',
            'com.google.android.tvrecommendations': 'android-tv-core-services-android-tv',
            'com.google.android.videos': 'google-play-movies',
            'com.google.android.videos.leanback': 'google-play-movies-tv-android-tv',
            'com.google.android.videos.vrmode': 'google-play-movies-tv-daydream',
            'com.google.android.webview': 'android-system-webview',
            'com.google.android.youtube': 'youtube',
            'com.google.android.youtube.tv': 'youtube-for-android-tv-android-tv',
            'com.google.earth': 'earth',
            'com.google.vr.vrcore': 'google-vr-services'}

    def get_google_app_feed_url(self, app):
        return self.host + f"/apk/google-inc/{app}/feed/"

    def get_apk_mirror_regex(self):
        return self.regex

    def get_apk_versions_url(self, app):
        print(f"Getting versions and links for {app}")
        feed_url = self.get_google_app_feed_url(app)

        feed_response = Requests.get(feed_url, headers=self.header)
        if feed_response.status_code != 200:
            print(f"Error getting versions for {app}, failed with status code {feed_response.status_code}")
            return None, None
        feed_response = feed_response.text
        soup = BeautifulSoup(feed_response, features="xml")
        app_link = None
        for link in soup.find_all('item'):
            app_link = link.find('link').text
            break
        if app_link is not None:
            html_response = Requests.get(app_link, headers=self.header)
            if html_response.status_code != 200:
                print(f"Error getting links for {app}, failed with status code {feed_response.status_code}")
                return None, None
            html_response = html_response.text
            soup = BeautifulSoup(html_response, features="html.parser")
            list_of_links = []
            for badges in soup.select('.apkm-badge'):
                # for Bundles the text is "BUNDLE"
                if badges.text == 'APK':
                    for prev in badges.previous_elements:
                        # noinspection PyUnresolvedReferences
                        if prev.name == 'a':
                            # noinspection PyUnresolvedReferences
                            list_of_links.append(self.host + prev['href'])
                            break
            version = soup.select('span.active.accent_color')
            if len(version) == 0:
                version = soup.select('a.active.accent_color')
            if len(version) > 0:
                version = version[0].text
                version = ''.join([c for c in version if c not in ['\t', '\n']])
                version = version.rstrip()
            return version, list_of_links
        else:
            return None, None

    def get_apk_mirror_dict(self, appset_list):
        nikgapps_package_names = {}
        for appset in appset_list:
            for package in appset.package_list:
                if package.package_name is not None and package.package_name in self.allApkMirrorNames:
                    apk_mirror_package = self.allApkMirrorNames[package.package_name]
                    version, list_of_links = self.get_apk_versions_url(apk_mirror_package)
                    version_code = ''.join([i for i in version if i.isdigit()])
                    g_dict = {"apk_mirror_package": apk_mirror_package, "version_code": version_code,
                              "title": package.title, "latest_version": version, "list_of_links": list_of_links}
                    nikgapps_package_names[package.package_name] = g_dict
        return nikgapps_package_names
