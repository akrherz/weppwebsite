"""Legacy stuff is fun."""
import sys
import datetime
import os
import numpy
from pyiem.util import get_dbconn, ncopen

SQUAW = get_dbconn("squaw")
scursor = SQUAW.cursor()

LOW_THRESHOLD = 0.10

storms = [0] * 4
for i in range(4):
    storms[i] = []


def process(ts, hrap_i, basinid):
    gx = (hrap_i - 1) % 173
    gy = int((hrap_i - 1) / 173)

    fp = ts.strftime(
        "/mnt/idep/data/rainfall/netcdf/daily/%Y/%m/%Y%m%d_rain.nc"
    )
    if not os.path.isfile(fp):
        return
    nc = ncopen(fp)
    p = nc.variables["rainfall_15min"]
    # Get me in inches
    minute15 = p[:, gy, gx] / 25.4
    hourly = numpy.zeros((24,), "f8")
    for i in range(24):
        hourly[i] = numpy.sum(minute15[i * 4 : (i * 4) + 4])

    STOPHR = -1
    bonusPrecip = 0
    stormnum = 0
    for hr in range(24):
        stp = 0
        STARTHR = hr
        while hr < 24 and hourly[hr] > 0 and hr > STOPHR:
            stp += hourly[hr]
            STOPHR = hr
            hr += 1
        # print hr, stp, STOPHR
        if stp > LOW_THRESHOLD:  # We have a storm
            storms[stormnum].append(
                {
                    "basinid": basinid,
                    "starthr": STARTHR,
                    "endhr": STOPHR,
                    "rain": stp,
                }
            )
            stormnum += 1
        else:
            bonusPrecip += stp

    if (
        bonusPrecip > LOW_THRESHOLD and len(storms[stormnum]) > 0
    ):  # Dump back into old storm....
        storms[stormnum][-1]["rain"] += bonusPrecip


def enterStorms(ts):
    for i in range(4):
        if len(storms[i]) == 0:  # No storms
            continue

        # Figure out what our ID will be for this storm
        sname = "A%s_%s" % (ts.strftime("%y%m%d"), i + 1)

        # Query the db, perhaps we already have an auto storm in there
        sql = "SELECT id from storms WHERE name = '%s'" % (sname,)
        scursor.execute(sql)
        if scursor.rowcount == 0:  # Need to get new ID, add entry for storm
            sql = "SELECT nextval('public.storms_id_seq'::text) as id"
            scursor.execute(sql)
            row = scursor.fetchone()
            sid = row[0]

            sql = """INSERT into storms(id, name, created, edited, notes) VALUES 
                    (%s, '%s', now(), now(), 'From squawStorms.py %s')""" % (
                sid,
                sname,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            )
            scursor.execute(sql)
            for j in range(13):
                sql = """INSERT into events(storm_id, basin_id, precip, onset, duration)
                    VALUES (%s, %s, 0, '1980-01-01', 0)""" % (
                    sid,
                    j,
                )
                scursor.execute(sql)

        else:
            row = scursor.fetchone()
            sid = row[0]

        # Okay, now we update
        for s in storms[i]:
            basin = s["basinid"]
            starthr = s["starthr"]
            endhr = s["endhr"]
            rain = s["rain"]

            duration = endhr - starthr
            sts = ts + datetime.timedelta(hours=starthr)
            sts = sts.replace(minute=0)
            sql = """UPDATE events SET precip = %.2f, onset = '%s', duration = %s 
                    WHERE storm_id = %s and basin_id = %s""" % (
                rain,
                sts.strftime("%Y-%m-%d %H:%M"),
                duration,
                sid,
                basin,
            )
            scursor.execute(sql)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        _YEAR = int(sys.argv[1])
        _MONTH = int(sys.argv[2])
        _DAY = int(sys.argv[3])
        ts = datetime.datetime(_YEAR, _MONTH, _DAY)
    else:
        ts = datetime.datetime.now() - datetime.timedelta(days=1)

    basins = [
        11829,
        11656,
        11831,
        11658,
        11659,
        11313,
        11139,
        11141,
        11488,
        10968,
        11316,
        10796,
        10797,
    ]
    for i in range(len(basins)):
        process(ts, basins[i], i)
    # print storms
    enterStorms(ts)

scursor.close()
SQUAW.commit()
SQUAW.close()
