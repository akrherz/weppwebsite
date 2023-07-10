import datetime

import matplotlib.pyplot as plt
import netCDF4
import numpy as np
from pyiem.plot import MapPlot

maxi = np.zeros((134, 173), "f")
sts = datetime.datetime(2010, 7, 22)
ets = datetime.datetime(2010, 7, 23)
now = sts
maxv = 0
while now < ets:
    nc = netCDF4.Dataset(
        now.strftime(
            "/mnt/idep/data/rainfall/netcdf/daily/%Y/%m/%Y%m%d_rain.nc"
        ),
        "r",
    )
    precip = np.max(nc.variables["rainfall_15min"][:], 0) / 24.5 * 4.0
    maxi = np.max([precip, maxi], 0)
    if np.max(precip) > 6:
        x1, y1 = np.unravel_index(maxi.argmax(), maxi.shape)
        maxv = np.max(maxi)
        print(now, maxv, np.max(precip))
        data = nc.variables["rainfall_15min"][:, x1, y1] / 24.5 * 4.0
        (fig, ax) = plt.subplots(1, 1)
        ax.bar(np.arange(24 * 4), data)
        ax.set_xlim(0, 96)
        for x in range(0, 97, 4):
            ax.axvline(x, c="k")
        fig.savefig("test.png")
        plt.close()
        # subprocess.call("xv test.png", shell=True)
    if now == sts:
        lat = nc.variables["latitude"][:]
        lon = nc.variables["longitude"][:]
    nc.close()
    now += datetime.timedelta(days=1)

m = MapPlot(
    sector="iowa",
    title="%s IDEP Peak Rainfall Intensity" % (sts.year,),
    subtitle="Based on 15 minute interval NEXRAD + NCEP Stage IV precipitation estimates",
)
m.pcolormesh(lon, lat, maxi, np.arange(0, 6.1, 0.25), units="inch per hour")
m.drawcounties()
m.postprocess(filename="example.png")
