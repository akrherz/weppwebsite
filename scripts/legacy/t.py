#!/mesonet/python/bin/python
# Need something to cache the historical images
# Daryl Herzmann 2 Oct 2004

import mx.DateTime, os, pg
mydb = pg.connect('wepp', 'db1.mesonet.agron.iastate.edu', 5432, user='mesonet')

s = mx.DateTime.DateTime(2002, 1,1)
e = mx.DateTime.DateTime(2004,10,2)
interval = mx.DateTime.RelativeDateTime(days=+1)

now = s
while (now < e):
  mydb.query("INSERT into erosion_log values ('%s')" % (now.strftime("%Y-%m-%d"),) )

  now += interval
