"""
  Generate a monthly shapefile of precipitation data
"""
from __future__ import print_function
import datetime
import shutil
import os
import sys

import shapefile
from pyiem.util import get_dbconn


def main(argv):
    """Go Main Go"""
    pgconn = get_dbconn('wepp')
    wcursor = pgconn.cursor()

    if len(argv) == 1:
        now = datetime.datetime.now() - datetime.timedelta(days=1)
        sts = now.replace(day=1)
        ets = (sts + datetime.timedelta(days=35)).replace(day=1)
    else:
        sts = datetime.datetime(int(argv[1]), 1, 1)
        ets = datetime.datetime(int(argv[1]), 12, 31)

    now = sts
    ohrap = {}
    wcursor.execute("SELECT hrap_i from hrap_utm ORDER by hrap_i ASC")
    for row in wcursor:
        ohrap[row[0]] = {'rain': 0, 'hours': 0, 'mrain': 0}

    hrapi = ohrap.keys()
    hrapi.sort()

    while now < ets:
        shapefilename = "%s_rain" % (now.strftime("%Y%m"), )
        shp = shapefile.Writer(shapeType=shapefile.POINT)
        shp.field("RAINFALL", 'F', 8, 2)
        shp.field("RAINHOUR", 'F', 8, 2)
        shp.field("RAINPEAK", 'F', 8, 2)

        wcursor.execute("""select hrap_i, rainfall /25.4 as rain,
            peak_15min /25.4 * 4 as mrain, hr_cnt / 4.0 as hours from
            monthly_rainfall_%s  WHERE valid = '%s'
            ORDER by hrap_i ASC
            """ % (now.strftime("%Y"), now.strftime("%Y-%m-%d")))

        hrap = ohrap
        for row in wcursor:
            hrap[row[0]] = {'rain': row[1],
                            'hours': row[3], 'mrain': row[2]}

        for i in range(len(hrapi)):
            key = hrapi[i]
            shp.point(1, 2)  # bogus
            shp.record(hrap[key]['rain'], hrap[key]['hours'],
                       hrap[key]['mrain'])

        shp.save(shapefilename)
        del shp
        outdir = "/mnt/idep/data/rainfall/shape/monthly/%s" % (now.year,)
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        shutil.copy("%s.dbf" % (shapefilename, ), outdir)
        os.unlink("%s.dbf" % (shapefilename,))
        os.unlink("%s.shp" % (shapefilename,))
        os.unlink("%s.shx" % (shapefilename,))

        now += datetime.timedelta(days=31)


if __name__ == '__main__':
    main(sys.argv)
