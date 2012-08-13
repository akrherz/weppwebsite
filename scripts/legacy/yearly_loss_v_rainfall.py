import iemdb
import numpy
WEPP = iemdb.connect('wepp', bypass=True)
wcursor = WEPP.cursor()

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

loss = []
rdays = []
wcursor.execute("""select model_twp, sum(avg_loss) * 4.463, 
sum(case when avg_precip > (1.25*25.4) then 1 else 0 end) from results_by_twp 
WHERE valid BETWEEN '2010-01-01' and '2011-01-01' GROUP by model_twp""")
for row in wcursor:
    if row[1] < 25:
        loss.append( row[1] )
        rdays.append( row[2] )
    
#ax.scatter(rdays, loss)
H2, xedges, yedges = numpy.histogram2d(rdays, loss, bins=(25, 25),range=[[0,25],[0,max(loss)]])
H2 = numpy.ma.array(H2.transpose())
H2.mask = numpy.where( H2 < 1, True, False)
res = ax.imshow(H2,  aspect='auto', interpolation='nearest')
ax.grid(True)
ax.set_ylim(-0.5,24.5)
ax.set_yticks( numpy.arange(0,25,5) )
ax.set_yticklabels( tuple(numpy.arange(0, int(max(loss)), int(max(loss))/5) ))
ax.set_ylabel("Tons per acre per year")
ax.set_xlabel("Days with >1.25 inch rainfall")
ax.set_xlim(-0.5,24.5)
ax.set_title("IDEP 2010 Total Soil Displacement\n versus days over 1.25 inch rainfall")
cb = fig.colorbar(res)
cb.ax.set_ylabel('Model Townships')

fig.savefig('idep2010.png')