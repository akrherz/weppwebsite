"""
Explore mapping IDEPv1 data direct from the database with matplotlib
"""
import sys

import matplotlib.cm as cm
import matplotlib.colors as mpcolors
import numpy as np
import psycopg2
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from pyiem.plot import MapPlot
from shapely.wkb import loads

DBCONN = psycopg2.connect(
    database="wepp", host="mesonet.agron.iastate.edu", user="nobody"
)
cursor = DBCONN.cursor()

yr = int(sys.argv[1])

m = MapPlot(sector="iowa", title="%s IDEPv1 Peak Rainfall Intensity" % (yr,))

cursor.execute(
    """

    SELECT ST_Transform(the_geom,4326), foo.val from
    (SELECT hrap_i, max(peak_15min) / 25.4 * 4.0 as val from daily_rainfall_%s
     GROUP by hrap_i) as foo 
    JOIN hrap_polygons p on (p.hrap_i = foo.hrap_i)

    --- select ST_Transform(the_geom,4326), total from 
    ---
    ---(SELECT model_twp, sum(avg_loss) * 4.463 as total from results_by_twp
    ---WHERE
    ---valid between '%s-01-01' and '%s-01-01' GROUP by model_twp) as foo
    ---
    ---JOIN iatwp t on (t.model_twp = foo.model_twp) ORDER by total DESC
    """
    % (yr, yr, yr + 1)
)

bins = np.array([0, 0.1, 0.5, 0.75, 1, 2, 3, 4, 5, 7, 10, 15, 20, 25])
bins = np.arange(0, 6.1, 0.5)
cmap = cm.get_cmap("jet")  # james2()
norm = mpcolors.BoundaryNorm(bins, cmap.N)
patches = []
for row in cursor:
    geom = loads(row[0].decode("hex"))
    for polygon in geom:
        a = np.asarray(polygon.exterior)
        x, y = m.map(a[:, 0], a[:, 1])
        a = zip(x, y)
        c = cmap(
            norm(
                [
                    float(row[1]),
                ]
            )
        )[0]
        p = Polygon(a, fc=c, ec="None", zorder=2, lw=0.1)
        patches.append(p)


m.ax.add_collection(PatchCollection(patches, match_original=True))
m.draw_colorbar(bins, cmap, norm, units="inches per hour")

m.drawcounties()
m.postprocess(filename="%srainfall.png" % (yr,))
