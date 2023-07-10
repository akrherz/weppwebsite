#!/usr/bin/env python
# Zero out rainfall for a day!!!

import shutil
import sys

import mx.DateTime

sts = mx.DateTime.DateTime(
    int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
)
ets = sts + mx.DateTime.RelativeDateTime(days=1)
interval = mx.DateTime.RelativeDateTime(minutes=+15)
now = sts + interval
while now <= ets:
    gts = now.gmtime()
    fp = gts.strftime("product/%Y/%Y%m%d/IA%Y%m%d_%H%M.dat")
    print(fp)
    shutil.copyfile("../iemrainfall/lib/empty.hrap", fp)
    now += interval
