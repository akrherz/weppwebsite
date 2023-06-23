#!/usr/bin/env python
# Generate a shapefile from our current understanding of points
# Daryl Herzmann 21 Jan 2003
#  20 Feb 2003:	Insert this information into the spatial DB as well

import dbflib
import pg
import shapelib

mydb = pg.connect("wepp")

points = 23182
lats = [0] * points
lons = [0] * points

lat0 = 40.000
lon0 = -97.000
latn = 44.000
lonn = -89.000
x = 173.0000
y = 134.0000
dlat = (lat0 - latn) / y
dlon = (lon0 - lonn) / x

dbf = dbflib.create("precip_points")
dbf.add_field("SID", dbflib.FTString, 1, 0)
dbf.add_field("SITE_NAME", dbflib.FTString, 1, 0)

shp = shapelib.create("precip_points", shapelib.SHPT_POINT)

for i in range(points):
    row = i / int(x)
    col = i % int(x)
    lat = lat0 - (row * dlat)
    lon = lon0 - (col * dlon)
    mydb.query(
        "INSERT into precip_points(point, geom) values( \
   "
        + str(i)
        + ", 'SRID=-1;POINT("
        + str(lon)
        + " "
        + str(lat)
        + ");')"
    )

    obj = shapelib.SHPObject(shapelib.SHPT_POINT, i, [[(lon, lat)]])
    shp.write_object(-1, obj)
    dbf.write_record(i, ("b", "b"))
    del obj
