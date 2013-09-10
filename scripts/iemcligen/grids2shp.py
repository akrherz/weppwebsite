"""
 Convert the 15 minute rainfall product into various other forms
"""
import datetime
import pytz
import shapelib
import dbflib
import sys
import os
import numpy
import traceback
import netCDF4
import subprocess

TMPFN = '/tmp/idep_rainfall.sql'

def createNETCDF(s):
	""" create a netcdf file """
	dirPre = s.strftime("/mnt/idep/data/rainfall/netcdf/daily/%Y/%m/")
	if not os.path.isdir(dirPre):
		os.makedirs(dirPre)
	fileName = dirPre + s.strftime("%Y%m%d_rain.nc")
	nc = netCDF4.Dataset(fileName, 'w')

	nc.createDimension("time", 96)
	nc.createDimension("hrap_i", 173)
	nc.createDimension("hrap_j", 134)

	tm = nc.createVariable("time", numpy.int, ('time',) ) 
	tm.units = "minutes since %s" % (s.strftime("%Y-%m-%d %H:%M"),)
	lat = nc.createVariable("latitude", numpy.float, ('hrap_j', 'hrap_i') )
	lon = nc.createVariable("longitude", numpy.float, ('hrap_j', 'hrap_i') )
	r15m = nc.createVariable("rainfall_15min", numpy.float, ('time', 'hrap_j', 'hrap_i') )
	r15m.units = "mm"
	r1d = nc.createVariable("rainfall_1day", numpy.float, ('hrap_j', 'hrap_i'))
	r1d.units = "mm"

	lat[:] = numpy.fromfile("/mnt/idep/GIS/lats.dat", sep=' ')
	lon[:] = numpy.fromfile("/mnt/idep/GIS/lons.dat", sep=' ')
	nc.sync()
	return nc, r1d, r15m, tm


def createSQLFILE(s, update_monthly):
	""" Create the SQL file for this date """
	sql = open(TMPFN, 'w')
	if update_monthly:
		sql.write("DELETE from monthly_rainfall_%s WHERE valid = '%s-01';\n" % (
											s.year, s.strftime("%Y-%m") ) )

	sql.write("DELETE from daily_rainfall_%s WHERE valid = '%s';\n" % (
										s.year, s.strftime("%Y-%m-%d") ) )
	sql.write("COPY daily_rainfall_%s FROM stdin;\n" % (s.year,))
	return sql

def createGIS(s):
	""" Create the shapefiles """
	dirname = s.strftime("/mnt/idep/data/rainfall/shape/daily/%Y/%m/")
	fname = s.strftime("%Y%m%d_rain")

	if not os.path.isdir(dirname):
		os.makedirs(dirname)
	dbf = dbflib.create(dirname + fname)
	dbf.add_field("RAINFALL", dbflib.FTDouble, 5, 2)

	shp = shapelib.create(dirname + fname, shapelib.SHPT_POINT)
	return shp, dbf

def main(year, month, day, update_monthly):
	""" Go main Go , we start at 12:15 AM and collect up a days worth """
	s = datetime.datetime(year,month,day,0,15)
	s = s.replace(tzinfo=pytz.timezone("America/Chicago"))
	e = s + datetime.timedelta(days=1)

	nc, nc_r1d, nc_r15m, nc_tm = createNETCDF(s)
	sql = createSQLFILE(s, update_monthly)
	shp, dbf = createGIS(s)
	rows = 134
	cols = 173
	rain15 = numpy.zeros( (96, rows, cols), numpy.float)
	interval = datetime.timedelta(minutes=+15)
	now = s
	i = 0
	while now < e:
		gts = now.astimezone(pytz.timezone('UTC'))
		fn = gts.strftime("/mnt/idep/data/rainfall/product/%Y/%Y%m%d/IA%Y%m%d_%H%M.dat")
		#print 'Processing: %s' % (fp,)
		nc_tm[i] = i * 15
		if os.path.isfile(fn):
			try:
				t = numpy.fromfile(fn, sep=' ')
				t = numpy.reshape(t, (rows, cols))
			except:
				print "Error with %s" % (fn,)
				traceback.print_exc(file=sys.stdout)
				print "------> Using zeros"
				t = numpy.zeros( (rows,cols), numpy.float)
		else:
			print "------> MISSING [%s] Using zeros" % (fn,)
			t = numpy.zeros( (rows,cols), numpy.float)
		rain15[i] = t
		now += interval
		i += 1
	max_rain15 = numpy.max(rain15, 0)
	hr_cnt = numpy.sum( numpy.where( rain15 > 0, 1, 0) , 0)
	nc_r15m[:] = rain15
	rain = numpy.sum(rain15, 0)
	nc_r1d[:] = rain
	nc.close()

	stringDate = s.strftime("%Y-%m-%d")
	lats = numpy.fromfile("/mnt/idep/GIS/lats.dat", sep=' ')
	lons = numpy.fromfile("/mnt/idep/GIS/lons.dat", sep=' ')
	i = 0
	max_rainfall = 0
	lats = numpy.reshape(lats, (rows, cols))
	lons = numpy.reshape(lons, (rows, cols))
	for row in range(rows):
		for col in range(cols):
			obj = shapelib.SHPObject(shapelib.SHPT_POINT, i, 
				[[(lons[row,col], lats[row,col])]] ) 
			shp.write_object(-1, obj)
			dbf.write_record(i, (rain[row][col] / 25.4 ,) )
			if rain[row][col] > 0:
				sql.write("%s\t%s\t%s\t%s\t%s\n" % (i +1, stringDate, 
					rain[row,col], max_rain15[row,col], hr_cnt[row,col]))
			if rain[row,col] > max_rainfall:
				max_rainfall = rain[row,col]
			i = i+1

	del(dbf)
	del(shp)
	sql.write("\.\n")
	nextmonth = s.replace(day=1) + datetime.timedelta(days=35)
	em = nextmonth.replace(day=1)
	sql.write("DELETE from rainfall_log WHERE valid = '%s' ;\n" % (
											s.strftime("%Y-%m-%d"),) )
	sql.write("""INSERT into rainfall_log (valid, max_rainfall) values ( 
	'%s', %s) ;\n""" % (s.strftime("%Y-%m-%d"), max_rainfall) )
	if update_monthly:
		sql.write("""INSERT into monthly_rainfall_%s (hrap_i, valid, rainfall,
		peak_15min, hr_cnt) 
        SELECT hrap_i, '%s-01', sum(rainfall), max(peak_15min), sum(hr_cnt) 
		from daily_rainfall_%s WHERE 
        valid >= '%s-01' and valid < '%s-01' GROUP by hrap_i;\n""" % (
		s.year, s.strftime("%Y-%m"), s.year, s.strftime("%Y-%m"), 
		em.strftime("%Y-%m") ) )


		sql.write("DELETE from yearly_rainfall WHERE valid = '%s-01-01';\n" \
		% (s.year) )
		sql.write("""INSERT into yearly_rainfall (hrap_i, valid, rainfall,
		peak_15min, hr_cnt) 
		SELECT hrap_i, '%s-01-01', sum(rainfall), max(peak_15min), sum(hr_cnt) 
		from monthly_rainfall_%s GROUP by hrap_i;\n""" % (s.year, s.year) )

if __name__ == "__main__":
	if len(sys.argv) >= 4:
		year = int(sys.argv[1])
		month = int(sys.argv[2])
		day = int(sys.argv[3])
		update_monthly = False
	else:
		# Run for yesterday
		ts = datetime.datetime.now() - datetime.timedelta(days=1)
		year, month, day = ts.year, ts.month, ts.day
		update_monthly = True
	if len(sys.argv) == 5:
		update_monthly = True

	main(year, month, day, update_monthly)
	if len(sys.argv) == 1:
		proc = subprocess.Popen("psql -h iemdb -f %s wepp" % (TMPFN,),
					shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stderr = proc.stderr.read()
		os.unlink(TMPFN)
