#!/mesonet/python/bin/python
# Output by township

import pg, shapelib, dbflib
from pyIEM import wellknowntext, iemdb
i = iemdb.iemdb()
mydb = i["wepp"]

twp = {}
rs = mydb.query("SELECT astext(the_geom) as t, model_twp from iatwp").dictresult()
for i in range(len(rs)):
	twp[ rs[i]["model_twp"] ] = rs[i]["t"]

rs = mydb.query("SELECT model_twp, sum(avg_loss) * 4.463 as loss, \
	sum(avg_precip) as rainfall, sum(avg_runoff) as runoff from \
	results_by_twp WHERE valid BETWEEN '2008-04-12' and '2008-06-13' \
	GROUP by model_twp").dictresult()

shp = shapelib.create("2008totals", shapelib.SHPT_POLYGON)
dbf = dbflib.create("2008totals")
dbf.add_field("LOSS", dbflib.FTDouble, 8, 4)
dbf.add_field("RUNOFF", dbflib.FTDouble, 8, 4)
dbf.add_field("PRECIP", dbflib.FTDouble, 8, 4)

for i in range(len(rs)):
	l = float(rs[i]["loss"])
	r = float(rs[i]["runoff"])
	p = float(rs[i]["rainfall"])
	m = rs[i]["model_twp"]

	f = wellknowntext.convert_well_known_text( twp[m] )
	obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, f )
	shp.write_object(-1, obj)
	dbf.write_record(i, (l,r,p) )
