"""
Generate a monthly shapefile of precipitation data
"""

import datetime
import os
import shutil
import sys
from collections import OrderedDict

import shapefile
from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()


def main(argv):
    """Go Main Go"""
    pgconn = get_dbconn("wepp")
    wcursor = pgconn.cursor()

    if len(argv) == 1:
        # Run for last month
        now = datetime.datetime.now() - datetime.timedelta(days=1)
        sts = now.replace(day=1)
        ets = (sts + datetime.timedelta(days=35)).replace(day=1)
    elif len(argv) == 2:
        sts = datetime.datetime(int(argv[1]), 1, 1)
        ets = datetime.datetime(int(argv[1]), 12, 31)
    elif len(argv) == 3:
        sts = datetime.datetime(int(argv[1]), int(argv[2]), 1)
        ets = (sts + datetime.timedelta(days=35)).replace(day=1)
    LOG.debug("sts: %s ets: %s", sts, ets)

    now = sts
    ohrap = OrderedDict()
    wcursor.execute("SELECT hrap_i from hrap_utm ORDER by hrap_i ASC")
    for row in wcursor:
        ohrap[row[0]] = {"rain": 0, "hours": 0, "mrain": 0}

    while now < ets:
        LOG.debug("processing %s", now)
        shapefilename = "%s_rain" % (now.strftime("%Y%m"),)

        wcursor.execute(
            """
            select hrap_i, rainfall /25.4 as rain,
            peak_15min /25.4 * 4 as mrain, hr_cnt / 4.0 as hours from
            monthly_rainfall  WHERE valid = %s
            ORDER by hrap_i ASC
        """,
            (now.strftime("%Y-%m-%d"),),
        )
        if wcursor.rowcount == 0:
            LOG.info("FATAL, found no rows for %s", now)
            return

        hrap = ohrap.copy()
        for row in wcursor:
            hrap[row[0]] = {"rain": row[1], "hours": row[3], "mrain": row[2]}

        with shapefile.Writer(shapefilename) as shp:
            shp.field("RAINFALL", "F", 8, 2)
            shp.field("RAINHOUR", "F", 8, 2)
            shp.field("RAINPEAK", "F", 8, 2)
            for key in ohrap:
                shp.point(1, 2)  # bogus
                # LOG.debug(hrap[key])
                shp.record(
                    hrap[key]["rain"], hrap[key]["hours"], hrap[key]["mrain"]
                )

        outdir = "/mnt/idep/data/rainfall/shape/monthly/%s" % (now.year,)
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        shutil.copy("%s.dbf" % (shapefilename,), outdir)
        for suffix in ["dbf", "shp", "shx"]:
            os.unlink("%s.%s" % (shapefilename, suffix))

        now += datetime.timedelta(days=31)


if __name__ == "__main__":
    main(sys.argv)
