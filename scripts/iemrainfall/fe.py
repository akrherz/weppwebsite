#!/usr/bin/env python

import mx.DateTime, os

sts = mx.DateTime.DateTime(2001,7,1)
ets = mx.DateTime.DateTime(2002,1,1)

now = sts
while (now < ets):
  print now
  os.system("./OLDDAY.csh %s" % (now.strftime("%Y %m %d"), ) )
  now += mx.DateTime.RelativeDateTime(days=+1)
