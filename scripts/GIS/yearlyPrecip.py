#!/mesonet/python/bin/python
# Pull out yearly precipitation

import pg, dbflib, mx.DateTime, shutil, sys, Numeric
from Scientific.IO.NetCDF import *
from Scientific.IO.ArrayIO import *
from pyIEM import iemdb
i = iemdb.iemdb()
wepp = i['wepp']

if (len(sys.argv) > 1):
    yr = sys.argv[1]
else:
    yr = mx.DateTime.now().year

ohrap = {}
rs = wepp.query("SELECT hrap_i from hrap_utm ORDER by hrap_i ASC").dictresult()
for i in range(len(rs)):
    ohrap[ int(rs[i]['hrap_i']) ] = {'rain': 0, 'hours': 0, 'mrain': 0}

hrapi = ohrap.keys()
hrapi.sort()

fileName = "%srain.nc" % (yr,)
nc = NetCDFFile(fileName, 'w')

nc.createDimension("hrap_i", 173)
nc.createDimension("hrap_j", 134)

lat = nc.createVariable("latitude", Numeric.Float, ('hrap_j', 'hrap_i') )
lon = nc.createVariable("longitude", Numeric.Float, ('hrap_j', 'hrap_i') )

ncrain = nc.createVariable("yrrain", Numeric.Float, ('hrap_j', 'hrap_i'))
ncrain.units = "inch"

lat.assignValue( readFloatArray("/mesonet/wepp/GIS/lats.dat") )
lon.assignValue( readFloatArray("/mesonet/wepp/GIS/lons.dat") )
nc.sync()


dbf = dbflib.create("%s_rain" % (yr, ) )
dbf.add_field("RAINFALL", dbflib.FTDouble, 8, 2)
dbf.add_field("RAINHOUR", dbflib.FTDouble, 8, 2)
dbf.add_field("RAINPEAK", dbflib.FTDouble, 8, 2)
    
rs = wepp.query("select hrap_i, sum(rainfall) /25.4 as rain, \
	max(peak_15min) /25.4 * 4 as mrain, sum(hr_cnt) / 4.0 as hours from \
	monthly_rainfall_%s  \
        GROUP by hrap_i ORDER by hrap_i ASC" % (yr,) ).dictresult()

hrap = ohrap
for i in range(len(rs)):
    #print rs[i]
    hrap[ int(rs[i]['hrap_i']) ]= {'rain': float(rs[i]['rain']), \
           'hours': float(rs[i]['hours']), 'mrain': float(rs[i]['mrain']) }

rain = Numeric.zeros( (134 * 173), Numeric.Float)
for i in range(len(hrapi)):
    key = hrapi[i]
    dbf.write_record(i, (hrap[key]['rain'], hrap[key]['hours'],\
		hrap[key]['mrain'] ) )
    rain[i] = hrap[key]['rain']

rain = Numeric.resize(rain, (134,173))
ncrain.assignValue(rain)
nc.close()

del dbf
shutil.copy("static/hrap_polygon_4326.shp", "%s_rain.shp" % (yr, ) )
shutil.copy("static/hrap_polygon_4326.shx", "%s_rain.shx" % (yr, ) )
#shutil.copy("static/hrap_polygon_4326.prj", "%srain.prj" % (yr, ) )

shutil.copy("%srain.nc" % (yr,), "/mesonet/wepp/data/rainfall/netcdf/yearly/")
shutil.copy("%s_rain.dbf" % (yr,), "/mesonet/wepp/data/rainfall/shape/yearly/")
