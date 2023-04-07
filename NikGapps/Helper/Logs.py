from datetime import datetime
import pytz


class Logs:

    @staticmethod
    def get_file_name(nikgappstype, android_version):
        current_time = Logs.get_current_time()
        return "NikGapps-" + nikgappstype + "-arm64-" + str(android_version) + "-" + current_time + ".zip"

    @staticmethod
    def get_current_time():
        tz_london = pytz.timezone('Europe/London')
        datetime_london = datetime.now(tz_london)
        return datetime_london.strftime("%Y%m%d")

    @staticmethod
    def get_path(user_name, android_code):
        tz_london = pytz.timezone('Europe/London')
        datetime_london = datetime.now(tz_london)
        return user_name + "/" + "NikGapps-" + str(android_code) + "/" + str(datetime_london.strftime("%d-%b-%Y"))
