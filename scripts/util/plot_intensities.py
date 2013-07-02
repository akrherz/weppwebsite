import netCDF4
import datetime
from pyiem.plot import MapPlot
import numpy

maxi = numpy.zeros((134,173), 'f')
sts = datetime.datetime(2013,1,1)
ets = datetime.datetime(2013,7,2)
now = sts
while now < ets:
    print now, numpy.max(maxi)
    nc = netCDF4.Dataset( now.strftime("/mnt/idep/data/rainfall/netcdf/daily/%Y/%m/%Y%m%d_rain.nc"), 'r')
    precip = numpy.max(nc.variables['rainfall_15min'][:],0) / 24.5 * 4.0
    maxi = numpy.max([precip, maxi], 0)
    if now == sts:
        lat = nc.variables['latitude'][:]
        lon = nc.variables['longitude'][:]
    nc.close()
    now += datetime.timedelta(days=1)

m = MapPlot(sector='iowa',
            title='2013 IDEP Peak Rainfall Intensity',
            subtitle='Based on 15 minute interval NEXRAD + NCEP Stage IV precipitation estimates')
m.pcolormesh(lon, lat, maxi, numpy.arange(0,6.1,0.25), units='inch per hour')
m.drawcounties()
m.postprocess(filename='example.png')