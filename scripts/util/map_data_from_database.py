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


def main():
    """Go main,"""
    DBCONN = psycopg2.connect(
        database="wepp", host="mesonet.agron.iastate.edu", user="nobody"
    )
    cursor = DBCONN.cursor()

    yr = int(sys.argv[1])

    m = MapPlot(sector="iowa", title=f"{yr} IDEPv1 Peak Rainfall Intensity")

    cursor.execute(
        """

        SELECT ST_Transform(the_geom,4326), foo.val from
        (SELECT hrap_i, max(peak_15min) / 25.4 * 4.0 as val from
        daily_rainfall_%s
        GROUP by hrap_i) as foo 
        JOIN hrap_polygons p on (p.hrap_i = foo.hrap_i)
        """
        % (yr,)
    )

    bins = np.arange(0, 6.1, 0.5)
    cmap = cm.get_cmap("jet")
    norm = mpcolors.BoundaryNorm(bins, cmap.N)
    patches = []
    for row in cursor:
        geom = loads(row[0].decode("hex"))
        for polygon in geom:
            a = np.asarray(polygon.exterior)
            x, y = m.map(a[:, 0], a[:, 1])
            a = zip(x, y, strict=True)
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


if __name__ == "__main__":
    main()
