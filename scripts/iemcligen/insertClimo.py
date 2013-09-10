#!/usr/bin/env python
# We need something to insert climo values into the database
# There is a problem with generating climate files before anything
# from the ag climate network comes in...
# 27 Apr 2004

import pg, mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()

sts = mx.DateTime.DateTime(2008,1,1)
ets = mx.DateTime.DateTime(2009,1,1)
interval = mx.DateTime.RelativeDateTime(days=+1)

climatedb = i['coop']
weppdb = i['wepp']

rs = climatedb.query("SELECT * from climate WHERE station = 'ia0200' \
	").dictresult()

db = {}
for i in range(len(rs)):
	d = mx.DateTime.strptime(rs[i]["valid"], "%Y-%m-%d")
	db[d] = rs[i]

now = sts
while (now < ets):
	dts = now + mx.DateTime.RelativeDateTime(year=2000)
	sql = "update climate_sectors SET high = %s, low = %s, dewp = %s \
		WHERE day = '%s'" % (db[dts]['high'], db[dts]['low'], \
		db[dts]['low'], now.strftime("%Y-%m-%d") )
	weppdb.query(sql)
	now += interval

