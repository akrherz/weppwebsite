#!/mesonet/python/bin/python
# Need something to cache the historical images
# Daryl Herzmann 2 Oct 2004

import mx.DateTime, os

s = mx.DateTime.DateTime(2013,1,1)
e = mx.DateTime.DateTime(2013,1,31)
interval = mx.DateTime.RelativeDateTime(days=+1)

now = s
cnt = 0
while (now < e):
  dir = "%s/%s" % (now.year, now.strftime("%m"))
  if (not os.path.isdir(dir)):
    os.makedirs(dir)
  print now
  for prod in ("rainfall_in", "avg_loss_acre", "avg_runoff_in", "vsm"):
    url = "http://wepp.mesonet.agron.iastate.edu/GIS/plot.php?duration=daily&width=320&height=240&var=%s&dstr=%s" % (prod, now.strftime("%m/%d/%Y"))
    cmd = "wget -q -O %s/%s_daily_%s.png '%s'" % (dir, now.strftime("%d"), prod, url)
    #cmd = "wget -O frames/%05i.png '%s'" % (cnt, url)
    os.system(cmd)
  cnt += 1
  now += interval
