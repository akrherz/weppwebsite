#!/usr/bin/env python
# Pull out yearly precipitation

import shutil

import dbflib
from pyIEM import iemdb
from Scientific.IO.ArrayIO import *
from Scientific.IO.NetCDF import *

i = iemdb.iemdb()
wepp = i["wepp"]

ohrap = {}
rs = wepp.query("SELECT hrap_i from hrap_utm ORDER by hrap_i ASC").dictresult()
for i in range(len(rs)):
    ohrap[int(rs[i]["hrap_i"])] = {"rain": 0, "hours": 0, "mrain": 0}

hrapi = ohrap.keys()
hrapi.sort()

dbf = dbflib.create("rain")
dbf.add_field("RAINFALL", dbflib.FTDouble, 8, 2)
dbf.add_field("RAINHOUR", dbflib.FTDouble, 8, 2)
dbf.add_field("RAINPEAK", dbflib.FTDouble, 8, 2)

rs = wepp.query(
    "select hrap_i, sum(rainfall) /25.4 as rain, \
	max(peak_15min) /25.4 * 4 as mrain, sum(hr_cnt) / 4.0 as hours from \
	monthly_rainfall_2007 WHERE valid IN ('2007-08-01','2007-09-01','2007-10-01') \
        GROUP by hrap_i ORDER by hrap_i ASC"
).dictresult()

hrap = ohrap
for i in range(len(rs)):
    # print rs[i]
    hrap[int(rs[i]["hrap_i"])] = {
        "rain": float(rs[i]["rain"]),
        "hours": float(rs[i]["hours"]),
        "mrain": float(rs[i]["mrain"]),
    }

for i in range(len(hrapi)):
    key = hrapi[i]
    dbf.write_record(
        i, (hrap[key]["rain"], hrap[key]["hours"], hrap[key]["mrain"])
    )


del dbf
shutil.copy("static/hrap_polygon_4326.shp", "rain.shp")
shutil.copy("static/hrap_polygon_4326.shx", "rain.shx")
