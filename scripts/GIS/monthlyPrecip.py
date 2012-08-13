#!/mesonet/python/bin/python
# Pull out yearly precipitation
# Daryl Herzmann 26 Jul 2004

import pg, dbflib, mx.DateTime, shutil, os, sys
mydb = pg.connect('wepp','iemdb')

if len(sys.argv) == 1:
  now = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)
  sts = now + mx.DateTime.RelativeDateTime(day=1)
  ets = sts + mx.DateTime.RelativeDateTime(months=1)
else:
  sts = mx.DateTime.DateTime(int(sys.argv[1]),1,1)
  ets = mx.DateTime.DateTime(int(sys.argv[1]),12,2)

interval = mx.DateTime.RelativeDateTime(months=+1)

now = sts
ohrap = {}
rs = mydb.query("SELECT hrap_i from hrap_utm ORDER by hrap_i ASC").dictresult()
for i in range(len(rs)):
    ohrap[ int(rs[i]['hrap_i']) ] = {'rain': 0, 'hours': 0, 'mrain': 0}

hrapi = ohrap.keys()
hrapi.sort()

while (now < ets):
    print "Hello Heather, I am here ", now
    dbfname = "monthlyrain/%s_rain" % (now.strftime("%Y%m"), )
    dbf = dbflib.create( dbfname )
    dbf.add_field("RAINFALL", dbflib.FTDouble, 8, 2)
    dbf.add_field("RAINHOUR", dbflib.FTDouble, 8, 2)
    dbf.add_field("RAINPEAK", dbflib.FTDouble, 8, 2)
    
    rs = mydb.query("select hrap_i, rainfall /25.4 as rain, \
	peak_15min /25.4 * 4 as mrain, hr_cnt / 4.0 as hours from \
	monthly_rainfall_%s  WHERE valid = '%s' \
        ORDER by hrap_i ASC" % (now.strftime("%Y"), \
        now.strftime("%Y-%m-%d") ) ).dictresult()

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
    outdir = "/mesonet/wepp/data/rainfall/shape/monthly/%s" % (now.year,)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    shutil.copy(dbfname+".dbf", outdir)
    shutil.copy("static/hrap_point_4326.shp", "monthlyrain/%s_rain.shp" % (now.strftime("%Y%m"), ) )
    shutil.copy("static/hrap_point_4326.shx", "monthlyrain/%s_rain.shx" % (now.strftime("%Y%m"), ) )
    shutil.copy("static/hrap_point_4326.prj", "monthlyrain/%s_rain.prj" % (now.strftime("%Y%m"), ) )

    now += interval

