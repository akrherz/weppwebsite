"""Combine the daily DBF files into a merged shapefile
Note that we can only have less than 255 columns in a dbf file
"""
import dbf
import datetime
import numpy as np

sts = datetime.date(2016, 1, 1)
ets = datetime.date(2016, 7, 11)
interval = datetime.timedelta(days=1)
now = sts

precip = np.zeros((23182, 192))

res = []
jday = 0
while now < ets:
    print now
    fn = now.strftime("%m/%Y%m%d_rain.dbf")
    d = dbf.Table(fn)
    d.open()
    i = 0
    for record in d:
        precip[i, jday] = record.rainfall
        i += 1
    res.append(now.strftime("%b%d") + " N(5,2)")
    now += interval
    jday += 1

comp = dbf.Table('combined', ";".join(res))
comp.open()
for i in range(23182):
    ar = tuple(precip[i, :])
    comp.append(ar)

comp.close()
