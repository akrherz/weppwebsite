"""
Generate summary shapefile of yearly precip, include monthly totals as attribs
"""

from __future__ import print_function

import datetime
import os
import shutil
import sys
from collections import OrderedDict

import netCDF4
import numpy
import shapefile
from pyiem.util import get_dbconn

BASEDIR = "/mnt/idep/data/rainfall"


def main(argv):
    """Go Main Go"""
    pgconn = get_dbconn("wepp")
    wcursor = pgconn.cursor()

    if len(argv) > 1:
        yr = argv[1]
    else:
        yr = datetime.datetime.now().year

    ohrap = OrderedDict()
    wcursor.execute("SELECT hrap_i from hrap_utm ORDER by hrap_i ASC")
    for row in wcursor:
        ohrap[row[0]] = {
            "rain": 0,
            "hours": 0,
            "mrain": 0,
            "jan_tot": 0,
            "feb_tot": 0,
            "mar_tot": 0,
            "apr_tot": 0,
            "may_tot": 0,
            "jun_tot": 0,
            "jul_tot": 0,
            "aug_tot": 0,
            "sep_tot": 0,
            "oct_tot": 0,
            "nov_tot": 0,
            "dec_tot": 0,
        }

    fileName = "%srain.nc" % (yr,)
    nc = netCDF4.Dataset(fileName, "w", format="NETCDF3_CLASSIC")

    nc.createDimension("hrap_i", 173)
    nc.createDimension("hrap_j", 134)

    lat = nc.createVariable("latitude", "f", ("hrap_j", "hrap_i"))
    lon = nc.createVariable("longitude", "f", ("hrap_j", "hrap_i"))

    ncrain = nc.createVariable("yrrain", "f", ("hrap_j", "hrap_i"))
    ncrain.units = "inch"

    lat[:] = numpy.genfromtxt("/mnt/idep/GIS/lats.dat")
    lon[:] = numpy.genfromtxt("/mnt/idep/GIS/lons.dat")
    nc.sync()

    shapefilename = "%s_rain" % (yr,)
    wcursor.execute(
        """
        select valid, hrap_i, rainfall / 25.4 as rain,
        peak_15min / 25.4 * 4 as mrain, hr_cnt / 4.0 as hours from
        monthly_rainfall_%s
    """
        % (yr,)
    )

    for row in wcursor:
        key = row[1]
        ohrap[key]["rain"] += row[2]
        ohrap[key]["hours"] += row[4]
        ohrap[key]["mrain"] = max(row[3], ohrap[key]["mrain"])
        mkey = "%s_tot" % (row[0].strftime("%b").lower(),)
        ohrap[key][mkey] = row[2]

    rain = numpy.zeros((134 * 173), "f")

    with shapefile.Writer(shapefilename) as shp:
        shp.field("RAINFALL", "F", 8, 2)
        shp.field("RAINHOUR", "F", 8, 2)
        shp.field("RAINPEAK", "F", 8, 2)
        shp.field("JAN_PREC", "F", 8, 2)
        shp.field("FEB_PREC", "F", 8, 2)
        shp.field("MAR_PREC", "F", 8, 2)
        shp.field("APR_PREC", "F", 8, 2)
        shp.field("MAY_PREC", "F", 8, 2)
        shp.field("JUN_PREC", "F", 8, 2)
        shp.field("JUL_PREC", "F", 8, 2)
        shp.field("AUG_PREC", "F", 8, 2)
        shp.field("SEP_PREC", "F", 8, 2)
        shp.field("OCT_PREC", "F", 8, 2)
        shp.field("NOV_PREC", "F", 8, 2)
        shp.field("DEC_PREC", "F", 8, 2)

        for i, key in enumerate(ohrap):
            shp.point(1, 2)  # bogus
            shp.record(
                ohrap[key]["rain"],
                ohrap[key]["hours"],
                ohrap[key]["mrain"],
                ohrap[key]["jan_tot"],
                ohrap[key]["feb_tot"],
                ohrap[key]["mar_tot"],
                ohrap[key]["apr_tot"],
                ohrap[key]["may_tot"],
                ohrap[key]["jun_tot"],
                ohrap[key]["jul_tot"],
                ohrap[key]["aug_tot"],
                ohrap[key]["sep_tot"],
                ohrap[key]["oct_tot"],
                ohrap[key]["nov_tot"],
                ohrap[key]["dec_tot"],
            )
            rain[i] = ohrap[key]["rain"]

    rain = numpy.resize(rain, (134, 173))
    ncrain[:] = rain
    nc.close()

    fn = "%srain.nc" % (yr,)
    shutil.copyfile(fn, "%s/netcdf/yearly/%s" % (BASEDIR, fn))
    os.unlink(fn)
    fn = "%s_rain.dbf" % (yr,)
    shutil.copy(fn, "%s/shape/yearly/%s" % (BASEDIR, fn))
    os.unlink(fn)
    os.unlink("%s.shx" % (shapefilename,))
    os.unlink("%s.shp" % (shapefilename,))


if __name__ == "__main__":
    main(sys.argv)
