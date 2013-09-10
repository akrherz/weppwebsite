#!/usr/bin/env python
# Need to generate a shapefile with hourly rainfall totals in it!
# Daryl Herzmann 28 May 2004

import pg, shapelib, dbflib, re, mx.DateTime, sys
from Scientific.IO.ArrayIO import *
mydb = pg.connect("wepp", 'iemdb')

y = int(sys.argv[1])
m = int(sys.argv[2])
d = int(sys.argv[3])
day = mx.DateTime.DateTime(y, m, d)
fname = day.strftime("%Y%m%d")

hrap_shapes = {}
hrain = {}
rs = mydb.query("SELECT transform(the_geom, 4326) as the_geom, hrap_i from hrap_utm").dictresult()
for i in range(len(rs)):
	hrain[ int(rs[i]["hrap_i"]) ] = {"HRAP_I": int(rs[i]["hrap_i"]) }
	hrap_shapes[ int(rs[i]["hrap_i"]) ] = rs[i]["the_geom"]

shp = shapelib.create(fname, shapelib.SHPT_POLYGON)
dbf = dbflib.create(fname)


dbf.add_field("HRAP_I", dbflib.FTInteger, 8, 0)
dbf.add_field("R_01AM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_02AM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_03AM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_04AM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_05AM", dbflib.FTDouble, 5, 5)
dbf.add_field("R_06AM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_07AM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_08AM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_09AM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_10AM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_11AM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_12PM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_01PM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_02PM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_03PM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_04PM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_05PM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_06PM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_07PM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_08PM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_09PM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_10PM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_11PM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_12AM", dbflib.FTDouble, 5, 2)
dbf.add_field("R_DAY", dbflib.FTDouble, 5, 2)


interval = mx.DateTime.RelativeDateTime(minutes=+15)
now = day

d = 0
for i in range(24):
	t = 0
	for j in range(4):
		now += interval
		gts = now.gmtime()
		fp = gts.strftime("/wepp/rain_process/data/%Y/%Y%m%d/IA%Y%m%d_%H%M.dat")
		f = readFloatArray(fp)
		t = f + t
		d = f + d
	hrap_i = 1
	dbfkey = string.upper(now.strftime("R_%I%P"))
	for row in range(len(t)):
		for col in range(len(t[row])):
			if (hrain.has_key(hrap_i)):
				val = t[row][col] / 25.4
				hrain[hrap_i][dbfkey] = val
			hrap_i += 1

hrap_i = 1
for row in range(len(t)):
	for col in range(len(t[row])):
		if (hrain.has_key(hrap_i)):
			val = d[row][col] / 25.4
			hrain[hrap_i]["R_DAY"] = val
		hrap_i += 1

i = 0
for hrap_i in hrap_shapes.keys():
	s = hrap_shapes[hrap_i]
	vals = re.findall("\(\(\((.*)\)\)\)", s)
	geo = re.findall("([^ ]*) ([^,]*),?", vals[0])
	f = []
	for o in geo:
		f.append( tuple(map(float,o)) )
	obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, [f,] )
	h = hrain[hrap_i]
	#print h
	dbf.write_record(i, h)
	shp.write_object(-1, obj)
	del obj
	i += 1

