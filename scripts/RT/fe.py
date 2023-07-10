import subprocess

import mx.DateTime

sts = mx.DateTime.DateTime(2013, 6, 1)
ets = mx.DateTime.DateTime(2013, 6, 26)
interval = mx.DateTime.RelativeDateTime(minutes=1440)

now = sts
while now < ets:
    cmd = "python summarize.py %s" % (now.strftime("%Y %m %d"),)
    subprocess.call(cmd, shell=True)
    now += interval
