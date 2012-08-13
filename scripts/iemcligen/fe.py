#!/mesonet/python/bin/python

import mx.DateTime, os, time

s = mx.DateTime.DateTime(2012,2, 1)
e = mx.DateTime.DateTime(2012,8, 11)
interval = mx.DateTime.RelativeDateTime(days=+1)

now =s
while (now<e):
  #cmd = "./grids2shp.py %s" % (now.strftime("%Y %m %d"),)
  #if ((now+interval).day == 1):
  #  cmd = "./grids2shp.py %s 1" % (now.strftime("%Y %m %d"),)
  cmd = "./build.py %s" % (now.strftime("%Y %m %d"),)
  os.system(cmd)
  #cmd = "psql -f rainfall.sql -h iemdb wepp"
  #os.system(cmd)
  print now
  #time.sleep(60)
  now += interval
