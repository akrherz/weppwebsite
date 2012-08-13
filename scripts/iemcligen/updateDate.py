#!/mesonet/python/bin/python
# Build out the climate files!

# Python imports
import cliFile, mx.DateTime, pg, os, sys, pickle, editclifile, cliRecord
from Scientific.IO.ArrayIO import *

# Connect to the WEPP database
mydb = pg.connect('wepp', 'iemdb', user='wepp')

# We call with args for the time we are interested in
if (len(sys.argv) == 4):
  yyyy, mm, dd = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
  ts = mx.DateTime.DateTime(yyyy, mm, dd)
else:
  ts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1, hour=0, minute=0)

# Globals
times = [0]*96
points = 23182
data = [0]*points
for i in range(points):
	data[i] = [0]*96
cl = {}
clh = {}

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

def main():
  # Lets load the rainfall first!
  loadClimate()
  loadClimateHeaders()

  # Load up rainfall polygons we wish to process
  rs = mydb.query("SELECT mgtzone, hrap_i from hrap_polygons \
    WHERE used = 't'").dictresult()
  processedPoints = 0
  for i in range(len(rs)):
    hrap_i = int(rs[i]['hrap_i'])
    mgtzone = rs[i]['mgtzone']
    cf = editclifile.editclifile('clifiles/%s.dat' % (hrap_i,) )
    cr = cliRecord.cliRecord(ts)
    cr.CLset(cl[mgtzone][0])
    cf.editDaySavePrecip(ts, cr)
    del(cf)
    del(cr)

main()
