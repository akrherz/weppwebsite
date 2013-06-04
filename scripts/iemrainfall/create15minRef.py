
import mx.DateTime
import os
import sys
import shutil

#sts = mx.DateTime.now()

if (len(sys.argv) != 6):
	print "Usage: python create15minRef.py RAD YYYY MM DD HR"
	sys.exit(0)

rad = sys.argv[1]
yyyy = int(sys.argv[2])
mm = int(sys.argv[3])
dd = int(sys.argv[4])
hr = int(sys.argv[5])

ts = mx.DateTime.DateTime(yyyy,mm,dd,hr)

files = {0: "", 1: "", 2: "", 3: ""}
fcnt = {0: 0, 1: 0, 2: 0, 3: 0}
fbin = {0: 15, 1: 30, 2: 45, 3: 60}
# We look for radar data files, if found, we add them to dicts
if (yyyy >= 2002):
	for mi in range(60):
		bin = mi / 15
		t = ts + mx.DateTime.RelativeDateTime(minutes=+mi)
		fp = "tmp/%s_NCR_%s.ras" % (rad, t.strftime("%Y%m%d_%H%M") )
		if (os.path.isfile(fp)):
			files[bin] += "%s\n" % (fp,)
			fcnt[bin] += 1

for k in fbin.keys():
	t = ts + mx.DateTime.RelativeDateTime(minutes=+ fbin[k])
	fp = "tmp/%s_%s.files15" % (rad, fbin[k])
	o = open(fp, 'w')
	o.write(files[k])
	o.close()
	os.system("bin/create15minutes %s %i > tmp/junk.dat" % (fp, fcnt[k]) )
	if not (os.path.isfile("SDUS53_RAIN.txt")):
		print rad, fbin[k]
	os.rename("SDUS53_RAIN.txt", "tmp/%s_RAIN_%s.dat" % (rad, fbin[k]) )

	if not (os.path.isfile("nexrad_hrap/HRAP_RAIN_%s" % (fbin[k],) ) ):
		shutil.copy("lib/empty.hrap", 
			"nexrad_hrap/HRAP_RAIN_%s" % (fbin[k],) )
	os.system("bin/createHRAP lib/K%s.txt tmp/%s_RAIN_%s.dat nexrad_hrap/HRAP_RAIN_%s" % (
													rad, rad, fbin[k], fbin[k]) )

