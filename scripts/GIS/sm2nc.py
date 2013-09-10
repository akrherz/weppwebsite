#!/usr/bin/env python

import Ngl
import Numeric
from Scientific.IO.NetCDF import *

from pyIEM import iemdb
i = iemdb.iemdb()
wepp = i['wepp']

lats = []
lons = []
s10cm = []
s20cm = []
vsm = []

rs = wepp.query("select x(centroid(transform(the_geom,4326))), y(centroid(transform(the_geom,4326))), vsm, s10cm, s20cm from iatwp i, waterbalance_by_twp w WHERE i.model_twp = w.model_twp and w.valid = 'YESTERDAY'").dictresult()

for i in range(len(rs)):
  lons.append( float(rs[i]['x']) )
  lats.append( float(rs[i]['y']) )
  s10cm.append( float(rs[i]['s10cm']) )
  s20cm.append( float(rs[i]['s20cm']) )
  vsm.append( float(rs[i]['vsm']) )

# Lets grid!
numxout = 35
numyout = 30
xmin    = min(lons) - 0.25
ymin    = min(lats) - 0.25
xmax    = max(lons) + 0.25
ymax    = max(lats) + 0.25

xc      = (xmax-xmin)/(numxout-1)
yc      = (ymax-ymin)/(numyout-1)

xo = xmin + xc*Numeric.arange(0,numxout)
yo = ymin + yc*Numeric.arange(0,numyout)
g_s10cm = Ngl.natgrid(lons, lats, s10cm, xo, yo)
g_s20cm = Ngl.natgrid(lons, lats, s20cm, xo, yo)
g_vsm = Ngl.natgrid(lons, lats, vsm, xo, yo)

# Write NetCDF
nc = NetCDFFile('iem_soilm.nc', 'w')
nc.createDimension('latitude', numyout)
nc.createDimension('longitude', numxout)

la = nc.createVariable('latitude', Numeric.Float, ('latitude',) )
la.units = 'degrees_north'
lo = nc.createVariable('longitude', Numeric.Float, ('longitude',) )
lo.units = 'degrees_east'

nc_s10cm = nc.createVariable('s10cm', Numeric.Float, ('longitude','latitude') )
nc_s10cm.units = 'millimeters'
nc_s10cm.long_name = '0-10 cm soil water'

nc_s20cm = nc.createVariable('s20cm', Numeric.Float, ('longitude','latitude') )
nc_s20cm.units = 'millimeters'
nc_s20cm.long_name = '10-20 cm soil water'

nc_vsm = nc.createVariable('vsm', Numeric.Float, ('longitude','latitude') )
nc_vsm.units = 'percent'
nc_vsm.long_name = 'Root Zone Volumetric Soil Moisture'

la.assignValue( yo )
lo.assignValue( xo )
nc_s10cm.assignValue( g_s10cm )
nc_s20cm.assignValue( g_s20cm )
nc_vsm.assignValue( g_vsm )

nc.close()
