#!/usr/bin/env python
# Get solar from ISU AgClimate network and update DB
# Daryl Herzmann 4 Mar 2003

import mx.DateTime
from pyIEM import iemdb

i = iemdb.iemdb()
mydb = i["campbelldaily"]
wepp = i["wepp"]

s = mx.DateTime.DateTime(1999, 1, 1)
e = mx.DateTime.DateTime(2000, 1, 1)
interval = mx.DateTime.RelativeDateTime(days=+1)

now = s

cref = {
    1: "a138019",
    2: "a134309",
    3: "a135879",
    4: "a131299",
    5: "a130209",
    6: "a131329",
    7: "a134759",
    8: "a131559",
    9: "a131909",
}
# cref = {1: 'a130209', 2: 'a130209', 3: 'a130209',
#        4: 'a130209', 5: 'a130209', 6: 'a130209',
#        7: 'a130209', 8: 'a130209', 9: 'a130209'}

# c80 is solar rad

last_value = "99"
while now < e:
    for sector in cref.keys():
        st = cref[sector]
        tbl = st + "_" + now.strftime("%Y")
        day = now.strftime("%Y-%m-%d")
        rs = mydb.query(
            "SELECT c80 from "
            + tbl
            + " WHERE \
     day = '"
            + day
            + "' "
        ).dictresult()
        if len(rs) > 0 and float(rs[0]["c80"]) > 0:
            rad = str(rs[0]["c80"])
            last_value = rad
        else:
            rad = last_value
        last_day = (now - mx.DateTime.RelativeDateTime(years=4)).strftime(
            "%Y-%m-%d"
        )
        wepp.query(
            "UPDATE climate_sectors SET rad = '"
            + rad
            + "' \
       WHERE day = '"
            + day
            + "' and sector = "
            + str(sector)
            + " "
        )

    now = now + interval
