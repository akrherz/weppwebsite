#!/mesonet/python/bin/python
# Need something to cache the historical images
# Daryl Herzmann 2 Oct 2004

import mx.DateTime, os

s = mx.DateTime.DateTime(1997,1,1)
e = mx.DateTime.DateTime(2002,1,1)
interval = mx.DateTime.RelativeDateTime(days=+1)

now = s
while (now < e):
  dir = "%s/%s" % (now.year, now.strftime("%m"))
  if (not os.path.isdir(dir)):
    os.makedirs(dir)
  for prod in ("rainfall_in", "avg_loss_acre", "avg_runoff_in"):
    url = "http://wepp.mesonet.agron.iastate.edu/GIS/plot.php?duration=daily&width=320&height=240&var=%s&dstr=%s" % (prod, now.strftime("%m/%d/%Y"))
    cmd = "wget -O %s/%s_daily_%s.png '%s'" % (dir, now.strftime("%d"), prod, url)
    os.system(cmd)

  now += interval
