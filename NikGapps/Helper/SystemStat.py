import platform
import psutil
from datetime import datetime
import pytz


class SystemStat:

    @staticmethod
    def show_stats():
        mem = psutil.virtual_memory()
        total_ram_in_bytes = mem.total
        total_ram_in_gb = round(mem.total / 1073741824, 2)
        print("---------------------------------------")
        print("Ram: " + str(total_ram_in_bytes) + " bytes, " + str(total_ram_in_gb) + " Gb")
        print("---------------------------------------")
        print("Running on system: " + platform.system())
        print("---------------------------------------")
        local = datetime.now()
        print("Local:", local.strftime("%a, %m/%d/%Y, %H:%M:%S"))
        tz_ny = pytz.timezone('America/New_York')
        datetime_ny = datetime.now(tz_ny)
        print("NY:", datetime_ny.strftime("%a, %m/%d/%Y, %H:%M:%S"))



