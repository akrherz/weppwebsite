#!/usr/bin/env python
# Build the IEM climate database template
# Daryl Herzmann 4 Mar 2003

import mx.DateTime
from pyIEM import iemdb

i = iemdb.iemdb()
mydb = i["wepp"]

s = mx.DateTime.DateTime(2008, 1, 1)
e = mx.DateTime.DateTime(2009, 1, 1)

now = s

while now < e:
    day = now.strftime("%Y-%m-%d")
    for i in range(1, 10):
        mydb.query(
            "INSERT into climate_sectors(sector, day) VALUES \
     ("
            + str(i)
            + ", '"
            + day
            + "') "
        )
    now = now + mx.DateTime.RelativeDateTime(days=+1)
