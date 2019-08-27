import iemdb
WEPP = iemdb.connect("wepp")
wcursor = WEPP.cursor()
import mx.DateTime
import os
os.chdir("/mnt/idep/RT")
sts = mx.DateTime.DateTime(2014,1,1)
ets = mx.DateTime.DateTime(2014,1,20)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts

while now < ets:
  wcursor.execute("""SELECT count(*) from waterbalance_by_twp where
  valid = '%s'""" % (now.strftime("%Y-%m-%d"),))
  row = wcursor.fetchone()
  if row[0] < 1000:
    print now, row
    os.system("python /mesonet/www/apps/weppwebsite/scripts/RT/reprocessWB.py %s" % (now.strftime("%Y %m %d"),))
  now += interval
