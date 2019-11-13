"""Combine the daily DBF files into a merged shapefile
Note that we can only have less than 255 columns in a dbf file

    rsync -a mesonet@mesonet:/mnt/idep/data/rainfall/shape/daily/2019/. .
"""
from __future__ import print_function
import datetime

# note that dbf is a laptop local python thing for now
import dbf
import numpy as np


def main():
    """Go Main Go"""
    sts = datetime.date(2019, 3, 1)
    ets = datetime.date(2019, 9, 1)
    interval = datetime.timedelta(days=1)
    now = sts

    precip = np.zeros((23182, int((ets - sts).days) + 1))

    res = []
    jday = 0
    while now <= ets:
        print(now)
        fn = now.strftime("%m/%Y%m%d_rain.dbf")
        table = dbf.Table(fn)
        table.open()
        i = 0
        for record in table:
            precip[i, jday] = record.rainfall
            i += 1
        res.append(now.strftime("%b%d") + " N(5,2)")
        now += interval
        jday += 1

    comp = dbf.Table('combined', ";".join(res))
    comp.open(dbf.READ_WRITE)
    for i in range(23182):
        ar = tuple(precip[i, :])
        comp.append(ar)

    comp.close()


if __name__ == '__main__':
    main()
