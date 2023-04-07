import psycopg2
import datetime
import numpy as np

WEPP = psycopg2.connect(
    database="wepp", host="mesonet.agron.iastate.edu", user="nobody"
)
cursor = WEPP.cursor()

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(1, 1)

highlights = {2013: "b", 2010: "g", 2012: "r"}
d2 = np.zeros((16, 365), "f")

for i, year in enumerate(range(1997, 2014)):
    cursor.execute(
        """
     SELECT valid, avg(vsm) from waterbalance_by_twp 
     WHERE valid between '%s-01-01' and '%s-12-31' 
     GROUP by valid ORDER by valid ASC"""
        % (year, year)
    )

    x = []
    y = []
    for row in cursor:
        x.append(datetime.datetime(2000, row[0].month, row[0].day))
        y.append(row[1])
    y = np.array(y)
    print(year, np.average(y), np.max(y[-90:]), len(y))
    if highlights.has_key(year):
        ax.plot(
            x, y, label="%s" % (year,), c=highlights[year], zorder=2, lw=2.0
        )
    else:
        ax.plot(x, y, c="tan")
    if year == 2011:
        x2 = x
    if year < 2013:
        d2[i, : len(y)] = y[:365]

print(len(x2), len(np.average(d2, 0)))
ax.plot(x2, np.average(d2, 0), lw=2, c="k", label="Avg", zorder=3)
ax.grid(True)
ax.set_ylabel("Root Zone Volumetric Soil Moisture [%]")
ax.set_title(
    "Iowa Daily Erosion Project (WEPP Model) Volumetric Soil Moisture\n(1997-2013) Iowa Areal Averaged Root Zone Soil Moisture"
)
ax.legend(ncol=2, loc=3)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d\n%b"))

fig.savefig("test.ps")
import iemplot

iemplot.makefeature("test")
