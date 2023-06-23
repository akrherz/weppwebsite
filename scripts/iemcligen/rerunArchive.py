#!/usr/bin/env python
# This script will update the climate DB with new and exciting info!!
# Daryl Herzmann 4 Mar 2003

import mx.DateTime
import pg

mydb = pg.connect("wepp")
asosdb = pg.connect("asos", "10.10.10.10", 5432)

ts = mx.DateTime.DateTime(1997, 1, 1)
tbl = ts.strftime("t%Y")

cref = {
    "SUX": 1,
    "MCW": 2,
    "DBQ": 3,
    "DNS": 4,
    "DSM": 5,
    "CID": 6,
    "ICL": 7,
    "LWD": 8,
    "BRL": 9,
}

sql = (
    "SELECT station, date(valid) as day, \
  max(tmpf) as high, min(tmpf) as low, \
  avg(sknt) as wvl, avg(dwpf) as dewp \
  from "
    + tbl
    + " WHERE \
  station IN "
    + str(tuple(cref.keys()))
    + " \
  GROUP by station, day"
)
rs = asosdb.query(sql).dictresult()

for i in range(len(rs)):
    zone = cref[rs[i]["station"]]
    mydb.query(
        "UPDATE climate_sectors SET high = "
        + str(rs[i]["high"])
        + ", \
   low = "
        + str(rs[i]["low"])
        + ", wvl = "
        + str(rs[i]["wvl"])
        + ", \
   dewp = "
        + str(rs[i]["dewp"])
        + ", drct = 0 WHERE sector = "
        + str(zone)
        + " \
   and day = '"
        + rs[i]["day"]
        + "' "
    )
