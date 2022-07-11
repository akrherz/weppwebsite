"""
  $tsw[] = $parts[5] / $soildepth * 100;
  $t10sw[] = $parts[6] / 100 * 100;
  $t20sw[] = $parts[7] / 100 * 100;
  $et[] = floatval($parts[8]);
  soildepth 1524
"""
import datetime

d2012 = []
t2012 = []
d2013 = []
t2013 = []
d2010 = []
t2010 = []

for i, line in enumerate(open("/tmp/177144.wb")):
    if i < 21:
        continue
    tokens = line.strip().split()
    if tokens[2] == "2012":
        t2012.append(float(tokens[4]) / 1524.0 * 100.0)
        ts = datetime.date(2000, 1, 1) + datetime.timedelta(
            days=int(tokens[1]) - 1
        )
        d2012.append(ts)
    if tokens[2] == "2010":
        t2010.append(float(tokens[4]) / 1524.0 * 100.0)
        ts = datetime.date(2000, 1, 1) + datetime.timedelta(
            days=int(tokens[1]) - 1
        )
        d2010.append(ts)
    if tokens[2] == "2013":
        t2013.append(float(tokens[4]) / 1524.0 * 100.0)
        ts = datetime.date(2000, 1, 1) + datetime.timedelta(
            days=int(tokens[1]) - 1
        )
        d2013.append(ts)

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

(fig, ax) = plt.subplots(1, 1)

ax.plot(d2010, t2010, label="2010, Soy", lw=2.0)
ax.plot(d2012, t2012, label="2012, Soy", lw=2.0)
ax.plot(d2013[:237], t2013[:237], label="2013, Corn", lw=2.0)
ax.set_xlim(datetime.date(2000, 5, 1), datetime.date(2000, 10, 1))
ax.legend(loc=3)
ax.grid(True)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d\n%B"))
ax.set_title(
    "Iowa Daily Erosion Project Modelled Soil Moisture\nCorn/Soy Rotation on Clarion Soil near Rockwell City"
)
ax.set_ylabel("Root Zone (0 to 1.5m depth) Soil Moisture [%]")

fig.savefig("test.ps")
import iemplot

iemplot.makefeature("test")
