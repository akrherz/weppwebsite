"""
Actually rip at the wb output files and reprocess the data inside them...
"""

import datetime
import os
import sys

import psycopg2

WEPP = psycopg2.connect(database="wepp", host="iemdb")
wcursor = WEPP.cursor()

sts = datetime.datetime(1997, 1, 1)
now = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
d = now.strftime("%Y-%m-%d")
lookfor = now.strftime(" %-j %Y ")
# We need to look up soil depths!
soil_depths = {}
sql = """select c.id as id, n.soil_depth from combos c, nri n 
        WHERE c.nri_id = n.id"""
wcursor.execute(sql)
for row in wcursor:
    soil_depths[row[0]] = row[1]

fp = open("wb.sql", "w")

fp.write("DELETE from waterbalance WHERE valid = '%s';\n" % (d,))
fp.write("COPY waterbalance FROM stdin;\n")
processedLines = 1

miss = 0
for run_id in soil_depths.keys():
    fn = "/mnt/idep/RT/wb/%s.wb" % (run_id,)
    if not os.path.isfile(fn):
        miss += 1
        continue
    for line in open(fn):
        if line.find(lookfor) > 0:
            tokens = line.strip().replace("*", "0").split()
            (tsw, s10cm, s20cm, et) = tokens[-4:]
            vsm = float(tsw) / soil_depths[int(run_id)] * 100.0
            fp.write(
                "%s\t%s\t%5.2f\t%s\t%s\t%s\n"
                % (run_id, d, vsm, s10cm, s20cm, et)
            )
            if processedLines % 1000 == 0:
                fp.write("\.\nCOPY waterbalance from STDIN;\n")
            processedLines += 1
            break
fp.write("\.\n")
fp.close()

os.system("psql -f wb.sql -h iemdb wepp")
wcursor.execute("DELETE from waterbalance_by_twp WHERE valid = '%s'" % (d,))
wcursor.execute(
    "insert into waterbalance_by_twp (select '%s', "
    "model_twp, avg(vsm), stddev(vsm), 0, avg(s10cm), avg(s20cm), "
    "avg(et) from waterbalance, combos WHERE combos.id = waterbalance.run_id "
    "and waterbalance.valid = '%s' GROUP by model_twp)" % (d, d)
)
wcursor.execute("DELETE from waterbalance WHERE valid = '%s'" % (d,))

wcursor.close()
WEPP.commit()
WEPP.close()
