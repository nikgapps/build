from datetime import datetime
import pytz


def get_file_name(nikgappstype, android_version):
    tz_london = pytz.timezone('Europe/London')
    datetime_london = datetime.now(tz_london)
    current_time = datetime_london.strftime("%Y%m%d")
    return "NikGapps-" + nikgappstype + "-arm64-" + str(android_version) + "-" + current_time + ".zip"
