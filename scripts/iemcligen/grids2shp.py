"""
 Convert the 15 minute rainfall product into various other forms
"""
from __future__ import print_function
import datetime
import sys
import os
import subprocess
import traceback
import shutil
from io import BytesIO

import pytz
import shapefile
import numpy as np
from pyiem.datatypes import distance
from pyiem.util import utc, ncopen, logger
LOG = logger()
TMPFN = '/tmp/idep_rainfall.sql'
IDEP = "/mnt/idep/data/rainfall"


def create_netcdf(s):
    """ create a netcdf file """
    dirname = s.strftime(IDEP + "/netcdf/daily/%Y/%m/")
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    filename = dirname + s.strftime("%Y%m%d_rain.nc")
    nc = ncopen(filename, 'w')

    nc.createDimension("time", 96)
    nc.createDimension("hrap_i", 173)
    nc.createDimension("hrap_j", 134)

    tm = nc.createVariable("time", np.int, ('time',))
    tm.units = "minutes since %s" % (s.strftime("%Y-%m-%d %H:%M"),)
    lat = nc.createVariable("latitude", np.float, ('hrap_j', 'hrap_i'))
    lon = nc.createVariable("longitude", np.float, ('hrap_j', 'hrap_i'))
    r15m = nc.createVariable("rainfall_15min", np.float,
                             ('time', 'hrap_j', 'hrap_i'))
    r15m.units = "mm"
    r1d = nc.createVariable("rainfall_1day", np.float, ('hrap_j', 'hrap_i'))
    r1d.units = "mm"

    lats = np.fromfile("/mnt/idep/GIS/lats.dat", sep=' ')
    lat[:] = lats[0]
    lons = np.fromfile("/mnt/idep/GIS/lons.dat", sep=' ')
    lon[:] = lons[0]
    nc.sync()
    return nc, r1d, r15m, tm


def create_sql(s, update_monthly):
    """ Create the SQL file for this date """
    sql = open(TMPFN, 'w')
    if update_monthly:
        sql.write("""
        DELETE from monthly_rainfall_%s WHERE valid = '%s-01';
        """ % (s.year, s.strftime("%Y-%m")))

    sql.write("""
        DELETE from daily_rainfall_%s WHERE valid = '%s';
        COPY daily_rainfall_%s FROM stdin;
    """ % (s.year, s.strftime("%Y-%m-%d"), s.year))
    return sql


def create_gis(s):
    """ Create the shapefiles """
    dirname = s.strftime(IDEP + "/shape/daily/%Y/%m/")

    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    shpio = BytesIO()
    shxio = BytesIO()
    dbfio = BytesIO()

    shp = shapefile.Writer(shx=shxio, shp=shpio, dbf=dbfio)
    shp.field("RAINFALL", 'F', 5, 2)

    return shp, shxio, shpio, dbfio


def workflow(year, month, day, update_monthly):
    """ Go main Go , we start at 12:15 AM and collect up a days worth """
    # Getting a proper local timezone is oh so difficult
    sts = utc()
    sts = sts.astimezone(pytz.timezone("America/Chicago"))
    sts = sts.replace(year=year, month=month, day=day, hour=0, minute=15)
    ets = sts + datetime.timedelta(days=1)

    nc, nc_r1d, nc_r15m, nc_tm = create_netcdf(sts)
    sql = create_sql(sts, update_monthly)
    rows = 134
    cols = 173
    rain15 = np.zeros((96, rows, cols), np.float)
    interval = datetime.timedelta(minutes=+15)
    now = sts
    i = 0
    while now < ets:
        gts = now.astimezone(pytz.UTC)
        fn = gts.strftime(IDEP + "/product/%Y/%Y%m%d/IA%Y%m%d_%H%M.dat")
        # print('Processing: %s' % (fp,))
        nc_tm[i] = i * 15
        if os.path.isfile(fn):
            try:
                grid = np.fromfile(fn, sep=' ')
                grid = np.reshape(grid, (rows, cols))
            except:
                LOG.info("Error with %s", fn)
                traceback.print_exc(file=sys.stdout)
                LOG.info("------> Using zeros")
                grid = np.zeros((rows, cols), np.float)
        else:
            LOG.info("------> MISSING [%s] Using zeros", fn)
            grid = np.zeros((rows, cols), np.float)
        rain15[i] = grid
        now += interval
        i += 1
    max_rain15 = np.max(rain15, 0)
    hr_cnt = np.sum(np.where(rain15 > 0, 1, 0), 0)
    nc_r15m[:] = rain15
    rain = np.sum(rain15, 0)
    rain_inch = distance(rain, 'MM').value('IN')
    nc_r1d[:] = rain
    nc.close()

    strdate = sts.strftime("%Y-%m-%d")
    lats = np.fromfile("/mnt/idep/GIS/lats.dat", sep=' ')
    lons = np.fromfile("/mnt/idep/GIS/lons.dat", sep=' ')
    shp, _shxio, _shpio, dbfio = create_gis(sts)
    i = 0
    max_rainfall = 0
    lats = np.reshape(lats, (rows, cols))
    lons = np.reshape(lons, (rows, cols))
    for row in range(rows):
        for col in range(cols):
            shp.point(lons[row, col], lats[row, col])
            shp.record(rain_inch[row][col])
            if rain[row][col] > 0:
                sql.write(("%s\t%s\t%s\t%s\t%s\n"
                           ) % (i + 1, strdate, rain[row, col],
                                max_rain15[row, col], hr_cnt[row, col]))
            if rain[row, col] > max_rainfall:
                max_rainfall = rain[row, col]
            i = i+1

    basefn = sts.strftime("%Y%m%d_rain")
    with open("%s.dbf" % (basefn, ), 'wb') as fh:
        fh.write(dbfio.getvalue())
    # with open("%s.shx" % (basefn, ), 'wb') as fh:
    #    fh.write(shpio.getvalue())
    # with open("%s.shp" % (basefn, ), 'wb') as fh:
    #    fh.write(shxio.getvalue())
    storagedir = IDEP + sts.strftime("/shape/daily/%Y/%m")
    if not os.path.isdir(storagedir):
        os.makedirs(storagedir)
    shutil.move(basefn + ".dbf", storagedir)

    sql.write(r"\.\n")
    nextmonth = sts.replace(day=1) + datetime.timedelta(days=35)
    em = nextmonth.replace(day=1)
    sql.write("""
        DELETE from rainfall_log WHERE valid = '%s' ;
    """ % (sts.strftime("%Y-%m-%d"), ))
    sql.write("""
        INSERT into rainfall_log (valid, max_rainfall) values ('%s', %s);
    """ % (sts.strftime("%Y-%m-%d"), max_rainfall))
    if update_monthly:
        sql.write("""
            INSERT into monthly_rainfall_%s (
            hrap_i, valid, rainfall, peak_15min,
            hr_cnt) SELECT hrap_i, '%s-01', sum(rainfall), max(peak_15min),
            sum(hr_cnt) from daily_rainfall_%s WHERE
            valid >= '%s-01' and valid < '%s-01' GROUP by hrap_i;
        """ % (sts.year, sts.strftime("%Y-%m"), sts.year,
               sts.strftime("%Y-%m"), em.strftime("%Y-%m")))

        sql.write("""
            DELETE from yearly_rainfall WHERE valid = '%s-01-01';
        """ % (sts.year))
        sql.write("""
            INSERT into yearly_rainfall (hrap_i, valid, rainfall, peak_15min,
            hr_cnt) SELECT hrap_i, '%s-01-01', sum(rainfall), max(peak_15min),
            sum(hr_cnt) from monthly_rainfall_%s GROUP by hrap_i;
        """ % (sts.year, sts.year))


def main(argv):
    """Go Main Go"""
    if len(argv) >= 4:
        year = int(argv[1])
        month = int(argv[2])
        day = int(argv[3])
        update_monthly = False
    else:
        # Run for yesterday
        ts = datetime.datetime.now() - datetime.timedelta(days=1)
        year, month, day = ts.year, ts.month, ts.day
        update_monthly = True
    if len(argv) == 5:
        update_monthly = True

    workflow(year, month, day, update_monthly)
    if len(sys.argv) == 1:
        proc = subprocess.Popen("psql -h iemdb.local -f %s wepp" % (TMPFN,),
                                shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        proc.stderr.read()
        os.unlink(TMPFN)


if __name__ == "__main__":
    main(sys.argv)
