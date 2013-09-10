#!/usr/bin/env python
# Pull out yearly precipitation
# Daryl Herzmann 26 Jul 2004

import pg, dbflib, mx.DateTime, shutil, shapelib
from pyIEM import wellknowntext
mydb = pg.connect('wepp','iemdb')

sts = mx.DateTime.DateTime(2005,3,1)
ets = mx.DateTime.DateTime(2005,11,1)
interval = mx.DateTime.RelativeDateTime(days=+7)

now = sts
twp = {}
rs = mydb.query("SELECT astext(transform(the_geom,4326)) as t, model_twp from iatwp ORDER by model_twp ASC").dictresult()
for i in range(len(rs)):
        twp[ rs[i]["model_twp"] ] = rs[i]["t"]

while (now < ets):
    print "Hello Heather, I am here ", now
    shp = shapelib.create("weeklysm/%ssm" % (now.strftime("%Y%m%d"), ), shapelib.SHPT_POLYGON)
    dbf = dbflib.create("weeklysm/%ssm" % (now.strftime("%Y%m%d"), ) )
    dbf.add_field("S0-10CM", dbflib.FTDouble, 8, 2)
    dbf.add_field("S10-20CM", dbflib.FTDouble, 8, 2)
    dbf.add_field("VSM", dbflib.FTDouble, 8, 2)
    
    rs = mydb.query("select model_twp, avg(vsm) as v, \
	avg(s10cm) as s10, avg(s20cm) as s20 from \
	waterbalance_by_twp  WHERE valid >= '%s' and valid < '%s' \
        GROUP by model_twp ORDER by model_twp ASC" % ( \
        now.strftime("%Y-%m-%d"), (now+interval).strftime("%Y-%m-%d")\
        ) ).dictresult()

    for i in range(len(rs)):
        m = rs[i]['model_twp']
        f = wellknowntext.convert_well_known_text( twp[m] )
        obj = shapelib.SHPObject(shapelib.SHPT_POLYGON, 1, f )
        shp.write_object(-1, obj)
        dbf.write_record(i, (rs[i]['s10'],rs[i]['s20'],rs[i]['v']) )

    del dbf
    del shp
    shutil.copy("static/hrap_point_4326.prj", "weeklysm/%ssm.prj" % (now.strftime("%Y%m%d"), ) )

    now += interval

