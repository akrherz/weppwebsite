import iemdb
import matplotlib.pyplot as plt
import numpy

WEPP = iemdb.connect("wepp", bypass=True)
wcursor = WEPP.cursor()


fig = plt.figure()
ax = fig.add_subplot(111)

loss = []
rain = []
wcursor.execute(
    """select model_twp, avg_loss * 4.463, 
avg_precip / 25.4 from results_by_twp 
WHERE valid BETWEEN '2011-01-01' and '2012-01-01' and avg_precip > 5"""
)
for row in wcursor:
    loss.append(float(row[1]))
    rain.append(float(row[2]))

loss = numpy.array(loss)
rain = numpy.array(rain)


ax.scatter(rain, loss)
ax.grid(True)
ax.set_ylabel("Soil Displacement [Tons per acre per year]")
ax.set_xlabel("Daily Rainfall [inch]")
ax.set_xlim(0, max(rain) + 1)
ax.set_ylim(0, max(loss) + 1)
ax.set_title("IDEP 2011 Daily Soil Displacement vs Rainfall")
# cb = fig.colorbar(res)
# cb.ax.set_ylabel('Model Townships')

fig.savefig("idep2011.png")
