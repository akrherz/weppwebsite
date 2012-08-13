# Python imports
import cliFile
import mx.DateTime
import pg
import os
import sys
import pickle
import editclifile
import cliRecord
import netCDF4
import numpy

# Connect to the WEPP database
mydb = pg.connect('wepp', 'iemdb', user='wepp')

# We call with args for the time we are interested in
if (len(sys.argv) == 4):
	yyyy, mm, dd = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
	ts = mx.DateTime.DateTime(yyyy, mm, dd)
	insertJobQueue = 0
elif len(sys.argv) == 2:
	ts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1, hour=0, minute=0)
	insertJobQueue = 0
else:
	ts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1, hour=0, minute=0)
	insertJobQueue = 1

# Globals
times = [0]*96
points = 23182
data = [0]*points
for i in range(points):
	data[i] = [0]*96
cl = {}
clh = {}

def doBreakPoint(hrap_i):
	data15 = data[hrap_i - 1]
	threshold = 0.1 * 25.4  # Threshold is 2/10 of an inch
	accum = 0.00
	writeAccum = 0.00
	lastTime = 0
	lines = 0
	bkTxt = ""
	cliFrmt = "%-12s%-12.3f\n"

	rAccum = 0  # Running Accumulation
	tAccum = 0  # Total Accumulation
	for tstep in range(96):
		rAccum += data15[tstep]
		tAccum += data15[tstep]
		if (rAccum > threshold):
			bkTxt += cliFrmt % (times[tstep], tAccum)
			rAccum = 0
                                                                                
	if (rAccum > 0):
		bkTxt += cliFrmt % (times[tstep], tAccum)
                                                                                
                                                                                
	return bkTxt

def loadClimate():
	# Load up the climate data from the database
	idx = ['0', 'NW', 'NC', 'NE', 'WC', 'C', 'EC', 'SW', 'SC', 'SE']

	for i in range(1,10):
		cl[ idx[i] ] = mydb.query("SELECT * from climate_sectors WHERE \
			sector = %s and day = '%s'" \
			% (i, ts.strftime("%Y-%m-%d") ) ).dictresult()

def loadClimateHeaders():
	# Open up the headers for the climate files
	clh['NW'] = open('headers/1.dat', 'r').read()
	clh['NC'] = open('headers/2.dat', 'r').read()
	clh['NE'] = open('headers/3.dat', 'r').read()
	clh['WC'] = open('headers/4.dat', 'r').read()
	clh['C'] = open('headers/5.dat', 'r').read()
	clh['EC'] = open('headers/6.dat', 'r').read()
	clh['SW'] = open('headers/7.dat', 'r').read()
	clh['SC'] = open('headers/8.dat', 'r').read()
	clh['SE'] = open('headers/9.dat', 'r').read()

def loadTimes():
        times[0] = "00.14"
	for i in range(1,96):
		myts = ts + mx.DateTime.RelativeDateTime(seconds=+ i*900)
		hr = myts.strftime("%H")
		mi = int(myts.strftime("%M"))
		frac = mi / 60.0
		times[i] = "%s.%02i" % (hr, frac * 100)
	times[95] = "23.90"


#

def loadRainfall():
	for i in range(1,97):
		# Local Time....
		myts = ts + mx.DateTime.RelativeDateTime(seconds=+ i*900)
		# Need to convert this to GMT
		gts = myts.gmtime()
		# fRef = ts.strftime("data/"+jDay+"/io%H%M."+jDay+".dat")
		# fRef = ts.strftime("data/"+str(yr)+"/"+jDay+"/io%Y%m%d_%H%M.dat")
		fRef = gts.strftime("../data/rainfall/product/%Y/%Y%m%d/IA%Y%m%d_%H%M.dat")
		#print "Processing:", fRef
		try:
			f = numpy.fromfile(fRef, sep=' ')
			f = numpy.reshape(f, (134,173))
		except:
			print "Missing File!", fRef
			continue
		for row in range(134):
			for col in range(173):
				data[col + (row * 173)][i-1] = f[row,col]


def main():
	# Lets load the rainfall first!
	loadRainfall()
	loadClimate()
	loadClimateHeaders()
	loadTimes()

	# Load up rainfall polygons we wish to process
	rs = mydb.query("""SELECT mgtzone, hrap_i from hrap_polygons 
		WHERE used = 't'""").dictresult()
	processedPoints = 0
	for i in range(len(rs)):
		hrap_i = int(rs[i]['hrap_i'])
		mgtzone = rs[i]['mgtzone']
		bktxt = doBreakPoint(hrap_i)
		#if (len(bktxt) > 0 or len(sys.argv) == 4):
		cf = editclifile.editclifile('clifiles/%s.dat' % (hrap_i,) )
		cr = cliRecord.cliRecord(ts)
		cr.BPset(bktxt)
		cr.CLset(cl[mgtzone][0])
		cf.editDay(ts, cr)
		cf.write()
#		os.system("/home/ldm/bin/pqinsert clifiles/%s.dat" % (hrap_i,) )
		#if (insertJobQueue):
		#	mydb.query("INSERT into job_queue (combo_id) \
		#     SELECT id from combos WHERE hrap_i = %s " % (hrap_i,) )
		del(cf)
		del(cr)
		#if (processedPoints % 1000 == 0):
		#	print "PROCESS UPDATE:", processedPoints
		processedPoints += 1

	#print "build.py: %s clifiles changed!" % (processedPoints)
	if (insertJobQueue):
		mydb.query("DELETE from job_queue")
		mydb.query("INSERT into job_queue(combo_id) select id from combos")
		#mydb.query("REINDEX TABLE job_queue")
		#mydb.query("VACUUM full analyze  verbose job_queue")
main()
