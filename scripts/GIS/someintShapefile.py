#!/usr/bin/env python
# Daryl Herzmann 28 May 2004

import pg, shapelib, dbflib, re, mx.DateTime, sys, os
from Scientific.IO.ArrayIO import *
mydb = pg.connect("wepp", 'iemdb')

y = int(sys.argv[1])
m = int(sys.argv[2])
d = int(sys.argv[3])
day = mx.DateTime.DateTime(y, m, d, 12, 0)

m = int(sys.argv[4])
d = int(sys.argv[5])
day1 = mx.DateTime.DateTime(y, m, d, 12, 0)

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
dbf.add_field("RAINFALL", dbflib.FTDouble, 5, 2)


interval = mx.DateTime.RelativeDateTime(minutes=+15)
now = day

d = 0
while (now <= day1):
	now += interval
	gts = now.gmtime()
	fp = gts.strftime("/wepp/data/rainfall/product/%Y/%Y%m%d/IA%Y%m%d_%H%M.dat")
	print fp
	if (os.path.isfile(fp)):
		f = readFloatArray(fp)
	else:
		print "------> MISSING! Using zeros"
		f = Numeric.zeros( (134,173), Numeric.Float)

	d = f + d

hrap_i = 1
for row in range(len(d)):
	for col in range(len(d[row])):
		val = d[row][col] / 25.4
		hrain[hrap_i]["RAINFALL"] = val
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

