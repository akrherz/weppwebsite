
import mx.DateTime
import sys
import os

yyyy = int(sys.argv[1])
mm = int(sys.argv[2])
dd = int(sys.argv[3])
hr = int(sys.argv[4])

ts = mx.DateTime.DateTime(yyyy, mm, dd, hr)

rads = ""
prods = ""
for mi in [15,30,45,60]:
	t = ts + mx.DateTime.RelativeDateTime(minutes= + mi)
	fp = "nexrad_hrap/HRAP_RAIN_%s" % (mi,)
	rads += "%s\n" % (fp,)

	ofp = "/mesonet/wepp/data/rainfall/product/%s/%s/IA%s.dat" % (t.year, 
							t.strftime("%Y%m%d"), t.strftime("%Y%m%d_%H%M") )
	if (not os.path.isdir("/mesonet/wepp/data/rainfall/product/%s/%s" % (t.year, t.strftime("%Y%m%d") ) )):
		os.makedirs("/mesonet/wepp/data/rainfall/product/%s/%s" % (t.year, t.strftime("%Y%m%d") ) )
	prods += "%s\n" % (ofp,)

hts = ts + mx.DateTime.RelativeDateTime(hours=+1)

o = open("tmp/S4_files.dat", 'w')
o.write("%s\n" % (hts.strftime("ncep_hrap/S4_%Y%m%d%H"),) )
o.close()

o = open("tmp/combout.dat", 'w')
o.write(prods)
o.close()

o = open("tmp/NEX_files.dat", 'w')
o.write(rads)
o.close()

os.system("bin/combine")
