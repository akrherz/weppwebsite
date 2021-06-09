"""
 A straight copy of ISUAG solar radiation data to IDEPv1 climate sector data,
 if data is not found from the ISUAG network, then the previous year's value
 is used.  Lame yes, but will be improved with IDEPv2
"""
from __future__ import print_function
import sys
import datetime
from pyiem.util import get_dbconn

ISUAG = get_dbconn("isuag")
icursor = ISUAG.cursor()
WEPP = get_dbconn("wepp")
wcursor = WEPP.cursor()


cref = {
    1: ["DONI4", "SBEI4"],
    2: ["KNAI4"],
    3: ["NASI4"],
    4: ["CNAI4"],
    5: ["BOOI4", "AEEI4"],
    6: ["CIRI4"],
    7: ["OKLI4"],
    8: ["CHAI4", "GREI4"],
    9: ["CRFI4"],
}


# c80 is solar rad
def process(ts):
    for sector in cref.keys():
        day = ts.strftime("%Y-%m-%d")
        for st in cref[sector]:
            sql = """SELECT slrkj_tot_qc / 1000. from sm_daily
              WHERE valid = '%s' and station = '%s' and
              slrkj_tot_qc is not null
              """ % (
                day,
                st,
            )
            icursor.execute(sql)
            if icursor.rowcount == 1:
                break
        if icursor.rowcount == 0:
            print(
                ("Missing Solar for sector: %s station: %s")
                % (sector, cref[sector])
            )
            continue
        row = icursor.fetchone()
        # convert mj to langleys
        rad = row[0] * 23.9
        # Crude bounds
        if rad < 0.01 or rad > 800:
            print(
                (
                    "IDEPv1 updateSolar.py FAIL sector: %s "
                    "station: %s rad: %.1f"
                )
                % (sector, st, rad)
            )
            continue
        wcursor.execute(
            """UPDATE climate_sectors SET rad = %s
          WHERE day = %s and sector = %s """,
            (rad, day, sector),
        )


if __name__ == "__main__":
    ts = datetime.datetime.now() - datetime.timedelta(days=1)
    if len(sys.argv) == 4:
        ts = datetime.datetime(
            int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
        )
    process(ts)

    wcursor.close()
    WEPP.commit()
    WEPP.close()
