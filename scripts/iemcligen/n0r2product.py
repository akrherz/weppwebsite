"""
Convert my N0R reflectivity composites into precipitation
Steps :
  1. Compute n0r coordinates from hrap cells
  2. Sum up our three 5minute bins to generate precip
  3. remap back to HRAP Grid (for now)
"""
import os

import iemdb
import mx.DateTime
import numpy
from osgeo import gdal
from Scientific.IO.ArrayIO import writeArray

WEPP = iemdb.connect("wepp")
wcursor = WEPP.cursor()

# Bounds -97.68 38.80,-87.49 45.21
# x1020 y642
# upper left is 45.21 -97.68
wcursor.execute(
    """
  SELECT hrap_i, x(ST_Transform(ST_Centroid(the_geom),4326)),
  y(ST_Transform(ST_Centroid(the_geom),4326))
  from hrap_utm ORDER by hrap_i ASC
"""
)

n0r_x = numpy.zeros((134, 173), "i")
n0r_y = numpy.zeros((134, 173), "i")

i = 0
for row in wcursor:
    r = i / 173
    c = i % 173
    n0r_x[r, c] = int((-97.68 - row[1]) / -0.01)
    n0r_y[r, c] = int((45.21 - row[2]) / 0.01)
    i += 1

y0 = int((50.0 - 45.21) / 0.01)
x0 = int((-126.0 + 97.68) / -0.01)
y1 = y0 + 642
x1 = x0 + 1020


def do(gts):
    """
    Do our 15 minute interval thing
    """
    rain = numpy.zeros((642, 1020), "f")
    for m in [-10, -5, 0]:
        now = gts + mx.DateTime.RelativeDateTime(minutes=m)
        fp = now.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png"
        )
        if not os.path.isfile(fp):
            continue
        n0r = gdal.Open(fp, 0)
        n0rd = ((n0r.ReadAsArray())[y0:y1, x0:x1] - 6.0) * 5.0
        rain += (
            0.036 * (10 ** (0.0625 * numpy.where(n0rd > 65, 65, n0rd))) / 12.0
        )

    # Now we back query, augh
    data = numpy.zeros((134, 173), "f")
    for x in range(173):
        for y in range(134):
            data[y, x] = rain[n0r_y[y, x], n0r_x[y, x]]

    fn = gts.strftime("../data/rainfall/product/%Y/%Y%m%d/IA%Y%m%d_%H%M.dat")
    writeArray(data, fn, "w")


sts = mx.DateTime.DateTime(1999, 1, 1, 6, 0)
ets = mx.DateTime.DateTime(2002, 1, 1, 6, 0)
interval = mx.DateTime.RelativeDateTime(minutes=15)

now = sts
while now < ets:
    do(now)
    now += interval
