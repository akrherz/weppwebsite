#!/mesonet/python-2.4/bin/python
# Pull out yearly precipitation
# Daryl Herzmann 26 Jul 2004

import pg, dbflib, mx.DateTime, shutil
mydb = pg.connect('wepp','iemdb')

sts = mx.DateTime.DateTime(2006,3,1)
ets = mx.DateTime.DateTime(2006,11,1)
interval = mx.DateTime.RelativeDateTime(days=+1)

now = sts
ohrap = {}
rs = mydb.query("SELECT hrap_i from hrap_utm ORDER by hrap_i ASC").dictresult()
for i in range(len(rs)):
    ohrap[ int(rs[i]['hrap_i']) ] = {'rain': 0, 'hours': 0, 'mrain': 0}

hrapi = ohrap.keys()
hrapi.sort()

while (now < ets):
    print "Hello Heather, I am here ", now
    dbf = dbflib.create("dailyrain/%srain" % (now.strftime("%Y%m%d"), ) )
    dbf.add_field("RAINFALL", dbflib.FTDouble, 8, 2)
    dbf.add_field("RAINHOUR", dbflib.FTDouble, 8, 2)
    dbf.add_field("RAINPEAK", dbflib.FTDouble, 8, 2)
    
    rs = mydb.query("select hrap_i, rainfall /25.4 as rain, \
	peak_15min /25.4 * 4 as mrain, hr_cnt / 4.0 as hours from \
	daily_rainfall_%s  WHERE valid = '%s' \
        ORDER by hrap_i ASC" % (now.strftime("%Y"), \
        now.strftime("%Y-%m-%d") \
        ) ).dictresult()

    hrap = ohrap
    for i in range(len(rs)):
        #print rs[i]
        hrap[ int(rs[i]['hrap_i']) ]= {'rain': float(rs[i]['rain']), \
           'hours': float(rs[i]['hours']), 'mrain': float(rs[i]['mrain']) }

    for i in range(len(hrapi)):
        key = hrapi[i]
        dbf.write_record(i, (hrap[key]['rain'], hrap[key]['hours'],\
		hrap[key]['mrain'] ) )

    del dbf
    shutil.copy("static/hrap_point_4326.shp", "dailyrain/%srain.shp" % (now.strftime("%Y%m%d"), ) )
    shutil.copy("static/hrap_point_4326.shx", "dailyrain/%srain.shx" % (now.strftime("%Y%m%d"), ) )
    shutil.copy("static/hrap_point_4326.prj", "dailyrain/%srain.prj" % (now.strftime("%Y%m%d"), ) )

    now += interval

