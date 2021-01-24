#!/usr/bin/env python
import pytz
from datetime import datetime
import platform

print("Start of the Program")
print("---------------------------------------")
local = datetime.now()
print("Local:", local.strftime("%m/%d/%Y, %H:%M:%S"))

tz_NY = pytz.timezone('America/New_York')
datetime_NY = datetime.now(tz_NY)
print("NY:", datetime_NY.strftime("%m/%d/%Y, %H:%M:%S"))

tz_London = pytz.timezone('Europe/London')
datetime_London = datetime.now(tz_London)
print("London:", datetime_London.strftime("%m/%d/%Y, %H:%M:%S"))
print("---------------------------------------")
print("Running on platform: " + platform.system())
print("---------------------------------------")

print("End of the Program")
