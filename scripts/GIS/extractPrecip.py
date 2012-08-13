#!/mesonet/python-2.4/bin/python
# Pull out yearly precipitation
# Daryl Herzmann 26 Jul 2004

import pg, dbflib
mydb = pg.connect('wepp','iemdb')

dbf = dbflib.create("2008rain")
dbf.add_field("RAINFALL", dbflib.FTDouble, 8, 2)
dbf.add_field("RAINHOUR", dbflib.FTDouble, 8, 2)
dbf.add_field("RAINPEAK", dbflib.FTDouble, 8, 2)

rs = mydb.query("select hrap_i, sum(rainfall) /25.4 as rain, \
	sum(peak_15min) /25.4 * 4 as mrain, sum(hr_cnt) / 4.0 as hours from \
        daily_rainfall_2008 WHERE valid between '2008-04-12' and '2008-06-13' GROUP by hrap_i ORDER by hrap_i ASC").dictresult()
	#monthly_rainfall_2002 GROUP by hrap_i ORDER by hrap_i ASC").dictresult()

for i in range(len(rs)):
	#print rs[i]
	dbf.write_record(i, (float(rs[i]["rain"]), float(rs[i]["hours"]),\
		float(rs[i]["mrain"]) ) )
	#dbf.write_record(i, (float(rs[i]["rain"]), ) )
