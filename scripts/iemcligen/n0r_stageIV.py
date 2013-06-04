# Test out some ideas on using my nexrad composites to QC the stage IV precip

import osgeo.gdal as gdal
import osgeo.gdal_array
from osgeo.gdalconst import *
import numpy, mx.DateTime, os, shutil
from Scientific.IO.ArrayIO import readFloatArray

hrap = 8045
lon = -93.02
lat = 41.29
#hrap = 7890
#lat = 41.10
#lon = -92.15
row = int(hrap / 173)
col = hrap % 173
x = int(( -126.0 - lon ) / - 0.01 )
y = int(( 50.0 - lat ) / 0.01 )

sts = mx.DateTime.DateTime(1997,1,1,6)
ets = mx.DateTime.DateTime(1998,1,1,6)
interval = mx.DateTime.RelativeDateTime(minutes=5)

ntotal = 0
ptotal = 0
rain = 0
now = sts
while now < ets:
  fp = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png")
  if not os.path.isfile(fp):
    now += interval
    continue
  n0r = gdal.Open(fp, 0)
  n0rd = n0r.ReadAsArray()
  val = n0rd[y,x]
  dbz = (val - 6) * 5.0
  if dbz > -25:
    rain += (0.036 * (10 ** (0.0625 * dbz)) / 12.0) #mm/hr in mm/5min
  #print "   %s,%.1f,%.1f" %(now.strftime("%Y-%m-%d %H:%M"), val, (val -7) * 5.0)

  if now.minute % 15 == 0:
     fRef = now.strftime("../data/rainfall/product/%Y/%Y%m%d/IA%Y%m%d_%H%M.dat")
     f = readFloatArray(fRef)
#     print 'PRODUCT %5.2f NEXRAD %5.2f' % ( f[row][col] / 25.4 , rain / 25.4)
     ptotal += f[row][col] / 25.4
     ntotal += rain / 25.4
     rain = 0

  if now.hour == 6 and now.minute == 0:
     print '%s StageIV: %5.2f NEXRAD: %5.2f' % ((now - mx.DateTime.RelativeDateTime(hours=12)).strftime('%Y-%m-%d'), ptotal, ntotal)
     ptotal = 0
     ntotal = 0

  now += interval
