#!/mesonet/python/bin/python
# Need something to generate shapes!

import wellknowntext, pg, shapelib
from Scientific.IO.ArrayIO import *
mydb = pg.connect("wepp")


rs = mydb.query("SELECT hrap_i, transform(the_geom, 4326) as the_geom from hrap_utm ORDER by hrap_i ASC").dictresult()

shp = shapelib.create("hrap_polygon", shapelib.SHPT_POLYGON)

for i in range(len(rs)):
	s = rs[i]["the_geom"]
	f = wellknowntext.convert_well_known_text(s)

	obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, f )

	shp.write_object(-1, obj)

lats = readFloatArray("/wepp/GIS/lats.dat")
lons = readFloatArray("/wepp/GIS/lons.dat")

shp2 = shapelib.create("hrap_point", shapelib.SHPT_POINT)

for row in range(134):
	for col in range(173):
		obj = shapelib.SHPObject(shapelib.SHPT_POINT, 1, 
			[[(lons[row][col], lats[row][col])]] )
		shp2.write_object(-1, obj)


