""" """

# Python imports
import datetime
import sys

import cliRecord
import editclifile
import psycopg2
import psycopg2.extras

WEPP = psycopg2.connect(database="wepp", host="iemdb")
wcursor = WEPP.cursor(cursor_factory=psycopg2.extras.DictCursor)


# We call with args for the time we are interested in
if len(sys.argv) == 4:
    yyyy, mm, dd = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    ts = datetime.datetime(yyyy, mm, dd)
else:
    ts = datetime.datetime.now() - datetime.timedelta(days=1)
    ts = ts.replace(hour=0, minute=0, microsecond=0)

# Globals
times = [0] * 96
points = 23182
data = [0] * points
for i in range(points):
    data[i] = [0] * 96
cl = {}
clh = {}


def loadClimate():
    # Load up the climate data from the database
    idx = ["0", "NW", "NC", "NE", "WC", "C", "EC", "SW", "SC", "SE"]

    for i in range(1, 10):
        wcursor.execute(
            """SELECT * from climate_sectors WHERE 
          sector = %s and day = '%s'"""
            % (i, ts.strftime("%Y-%m-%d"))
        )
        row = wcursor.fetchone()
        cl[idx[i]] = row


def loadClimateHeaders():
    # Open up the headers for the climate files
    clh["NW"] = open("headers/1.dat", "r").read()
    clh["NC"] = open("headers/2.dat", "r").read()
    clh["NE"] = open("headers/3.dat", "r").read()
    clh["WC"] = open("headers/4.dat", "r").read()
    clh["C"] = open("headers/5.dat", "r").read()
    clh["EC"] = open("headers/6.dat", "r").read()
    clh["SW"] = open("headers/7.dat", "r").read()
    clh["SC"] = open("headers/8.dat", "r").read()
    clh["SE"] = open("headers/9.dat", "r").read()


def main():
    # Lets load the rainfall first!
    loadClimate()
    loadClimateHeaders()

    # Load up rainfall polygons we wish to process
    wcursor.execute(
        """SELECT mgtzone, hrap_i from hrap_polygons 
        WHERE used = 't'"""
    )
    for row in wcursor:
        hrap_i = row["hrap_i"]
        mgtzone = row["mgtzone"]
        cf = editclifile.editclifile(
            "/mnt/idep/data/clifiles/%s.dat" % (hrap_i,)
        )
        cr = cliRecord.cliRecord(ts)
        cr.CLset(cl[mgtzone])
        cf.editDaySavePrecip(ts, cr)
        del cf
        del cr


main()
