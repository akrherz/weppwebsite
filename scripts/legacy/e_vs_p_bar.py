import iemdb
import numpy

WEPP = iemdb.connect("wepp", bypass=True)
wcursor = WEPP.cursor()

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

loss = []
rain = []
#  avg_loss * 4.463
wcursor.execute(
    """select avg( avg_loss ), 
 round( (avg_precip / 2.54)::numeric, 0) as bin  from results_by_twp 
 WHERE valid BETWEEN '2011-01-01' and '2012-01-01' 
 and avg_precip > 5 GROUP by bin ORDER by bin ASC"""
)
for row in wcursor:
    loss.append(float(row[0]))
    rain.append(float(row[1]) * 2.54)

loss = numpy.array(loss)
rain = numpy.array(rain)


# ax.scatter(rdays, loss)
# H2, xedges, yedges = numpy.histogram2d(rdays, loss, bins=(25, 25),range=[[0,25],[0,max(loss)]])
# H2 = numpy.ma.array(H2.transpose())
# H2.mask = numpy.where( H2 < 1, True, False)
# res = ax.imshow(H2,  aspect='auto', interpolation='nearest')
ax.bar(rain, loss, width=2.54)
ax.grid(True)
# ax.set_ylim(-0.5,24.5)
# ax.set_yticks( numpy.arange(0,25,5) )
# ax.set_yticklabels( tuple(numpy.arange(0, int(max(loss)), int(max(loss))/5) ))
ax.set_ylabel("Soil Displacement [kg / m2]")
ax.set_xlabel("Daily Rainfall [mm]")
ax.set_xlim(0, max(rain) - 5)
ax.set_ylim(0, max(loss) + 0.1)
ax.set_title("IDEP 2011 Average Daily Soil Displacement vs Rainfall")
# cb = fig.colorbar(res)
# cb.ax.set_ylabel('Model Townships')

fig.savefig("idep2011_bar.png")
