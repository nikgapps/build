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
