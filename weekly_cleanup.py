#!/usr/bin/env python3
from time import sleep
from datetime import datetime, timedelta
from threading import Timer
import organize_photos_CLI

x=datetime.today()
y = x.replace(day=x.day, hour=1, minute=0, second=0, microsecond=0) + timedelta(days=1)
delta_t = y-x
secs = delta_t.total_seconds()

def start():
    organize_registered_folders()
try:
    t = Timer(secs, start)
    t.start()
except KeyboardInterrupt:
    pass
