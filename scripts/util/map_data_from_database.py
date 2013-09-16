'''
Explore mapping IDEPv1 data direct from the database with matplotlib
'''
from pyiem.plot import MapPlot, maue
from shapely.wkb import loads
import psycopg2
import sys
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.colors as mpcolors

DBCONN = psycopg2.connect(database='wepp', host='iemdb', user='nobody')
cursor = DBCONN.cursor()

yr = int(sys.argv[1])

m = MapPlot(sector='iowa',
            title='%s IDEPv1 Township Average Soil Displacement' % (yr,))

cursor.execute("""select ST_Transform(the_geom,4326), total from 
    
    (SELECT model_twp, sum(avg_loss) * 4.463 as total from results_by_twp WHERE
    valid between '%s-01-01' and '%s-01-01' GROUP by model_twp) as foo
    
    JOIN iatwp t on (t.model_twp = foo.model_twp) ORDER by total DESC
    """ % (yr, yr+1))

bins = np.array([0,0.1,0.5,0.75,1,2,3,4,5,7,10,15,20,25])
cmap = maue()
norm = mpcolors.BoundaryNorm(bins, cmap.N)
patches = []
for row in cursor:
    geom = loads( row[0].decode('hex') )
    for polygon in geom:
        a = np.asarray(polygon.exterior)
        x,y = m.map(a[:,0], a[:,1])
        a = zip(x,y)
        c = cmap( norm([float(row[1]),]) )[0]
        p = Polygon(a,fc=c,ec='None',zorder=2, lw=.1)
        patches.append(p)

          
m.ax.add_collection(PatchCollection(patches,match_original=True))
m.draw_colorbar(bins, cmap, norm, units='tons per acre')

m.drawcounties()
m.postprocess(filename='/tmp/%serosion.png' % (yr,))