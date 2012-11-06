"""
Generate summary shapefile of yearly precip, include monthly totals as attribs
"""

import dbflib
import mx.DateTime
import shutil
import sys
import numpy
import netCDF4
import iemdb
WEPP = iemdb.connect('wepp', bypass=True)
wcursor = WEPP.cursor()

if (len(sys.argv) > 1):
    yr = sys.argv[1]
else:
    yr = mx.DateTime.now().year

ohrap = {}
wcursor.execute("SELECT hrap_i from hrap_utm ORDER by hrap_i ASC")
for row in wcursor:
    ohrap[ row[0] ] = {'rain': 0, 'hours': 0, 'mrain': 0,
                                     'jan_tot': 0, 'feb_tot': 0, 'mar_tot': 0,
                                     'apr_tot': 0, 'may_tot': 0, 'jun_tot': 0,
                                     'jul_tot': 0, 'aug_tot': 0, 'sep_tot': 0,
                                     'oct_tot': 0, 'nov_tot': 0, 'dec_tot': 0}

hrapi = ohrap.keys()
hrapi.sort()

fileName = "%srain.nc" % (yr,)
nc = netCDF4.Dataset(fileName, 'w', mode='NETCDF3_CLASSIC')

nc.createDimension("hrap_i", 173)
nc.createDimension("hrap_j", 134)

lat = nc.createVariable("latitude", 'f', ('hrap_j', 'hrap_i') )
lon = nc.createVariable("longitude", 'f', ('hrap_j', 'hrap_i') )

ncrain = nc.createVariable("yrrain", 'f', ('hrap_j', 'hrap_i'))
ncrain.units = "inch"

lat[:] = numpy.genfromtxt("/mesonet/wepp/GIS/lats.dat")
lon[:] = numpy.genfromtxt("/mesonet/wepp/GIS/lons.dat")
nc.sync()


dbf = dbflib.create("%s_rain" % (yr, ) )
dbf.add_field("RAINFALL", dbflib.FTDouble, 8, 2)
dbf.add_field("RAINHOUR", dbflib.FTDouble, 8, 2)
dbf.add_field("RAINPEAK", dbflib.FTDouble, 8, 2)
dbf.add_field("JAN_PREC", dbflib.FTDouble, 8, 2)
dbf.add_field("FEB_PREC", dbflib.FTDouble, 8, 2)
dbf.add_field("MAR_PREC", dbflib.FTDouble, 8, 2)
dbf.add_field("APR_PREC", dbflib.FTDouble, 8, 2)
dbf.add_field("MAY_PREC", dbflib.FTDouble, 8, 2)
dbf.add_field("JUN_PREC", dbflib.FTDouble, 8, 2)
dbf.add_field("JUL_PREC", dbflib.FTDouble, 8, 2)
dbf.add_field("AUG_PREC", dbflib.FTDouble, 8, 2)
dbf.add_field("SEP_PREC", dbflib.FTDouble, 8, 2)
dbf.add_field("OCT_PREC", dbflib.FTDouble, 8, 2)
dbf.add_field("NOV_PREC", dbflib.FTDouble, 8, 2)
dbf.add_field("DEC_PREC", dbflib.FTDouble, 8, 2)

wcursor.execute("""select valid, hrap_i, rainfall / 25.4 as rain, 
	peak_15min / 25.4 * 4 as mrain, hr_cnt / 4.0 as hours from 
	monthly_rainfall_%s """ % (yr,) )

for row in wcursor:
    key = row[1] 
    ohrap[ key ]['rain'] += row[2] 
    ohrap[ key ]['hours'] += row[4]
    ohrap[ key ]['mrain'] = max(row[3], ohrap[ key ]['mrain'])
    mkey = "%s_tot" % (row[0].strftime("%b").lower(),)
    ohrap[ key ][ mkey ] = row[2]

rain = numpy.zeros( (134 * 173), 'f')
for i in range(len(hrapi)):
    key = hrapi[i]
    dbf.write_record(i, (ohrap[key]['rain'], ohrap[key]['hours'],
		ohrap[key]['mrain'], 
        ohrap[key]['jan_tot'],  ohrap[key]['feb_tot'], ohrap[key]['mar_tot'],
        ohrap[key]['apr_tot'],  ohrap[key]['may_tot'], ohrap[key]['jun_tot'],
        ohrap[key]['jul_tot'],  ohrap[key]['aug_tot'], ohrap[key]['sep_tot'],
        ohrap[key]['oct_tot'],  ohrap[key]['nov_tot'], ohrap[key]['dec_tot'],
        ) )
    rain[i] = ohrap[key]['rain']

rain = numpy.resize(rain, (134,173))
ncrain[:] = rain
nc.close()

del dbf
#shutil.copy("static/hrap_polygon_4326.shp", "%s_rain.shp" % (yr, ) )
#shutil.copy("static/hrap_polygon_4326.shx", "%s_rain.shx" % (yr, ) )
#shutil.copy("static/hrap_polygon_4326.prj", "%srain.prj" % (yr, ) )
fn = "%srain.nc" % (yr,)
shutil.copyfile(fn, "/mesonet/wepp/data/rainfall/netcdf/yearly/"+fn)
fn = "%s_rain.dbf" % (yr,)
shutil.copy(fn, "/mesonet/wepp/data/rainfall/shape/yearly/"+fn)
