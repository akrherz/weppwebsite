"""
"""
import psycopg2
import os
import re
import datetime
import sys

WEPP = psycopg2.connect(database="wepp", host="iemdb")
wcursor = WEPP.cursor()

upfact = {}
wcursor.execute(
    """select c.id, n.upfact from combos c, nri n 
      WHERE c.nri_id = n.id"""
)
for row in wcursor:
    upfact[row[0]] = row[1]

if len(sys.argv) == 4:
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    day = int(sys.argv[3])
else:
    its = datetime.datetime.now() - datetime.timedelta(days=1)
    year = its.year
    month = its.month
    day = its.day

ots = datetime.datetime(year, month, day)

files = os.listdir("env")

fp = open("insert.sql", "w")

fp.write(
    "DELETE from results WHERE valid = '%s';\n" % (ots.strftime("%Y-%m-%d"))
)
fp.write("COPY results FROM stdin;\n")

for filename in files:
    run_id = filename[:-4]
    o = open("env/" + filename, "r")
    for linenum, line in enumerate(o):
        if linenum < 3:
            continue
        tokens = line.split()
        try:
            ts = datetime.datetime(
                int(tokens[2]) + 1996, int(tokens[1]), int(tokens[0])
            )
        except:
            print(
                "processEvents file: %s line:%s tokens:%s"
                % (filename, linenum, tokens)
            )
            continue
        if ts != ots:
            continue
        trunoff = tokens[4]
        tloss = tokens[6]
        tprecip = tokens[3]
        fp.write(
            "%s\t%s\t%s\t%5.2f\t%s\n"
            % (
                run_id,
                ts.strftime("%Y-%m-%d"),
                trunoff,
                float(tloss) * upfact[int(run_id)],
                tprecip,
            )
        )

fp.write("\.\n")
fp.write(
    "DELETE from erosion_log WHERE valid = '%s';\n"
    % (ots.strftime("%Y-%m-%d"),)
)
fp.write(
    "INSERT into erosion_log (valid) VALUES ('%s'); \n"
    % (ots.strftime("%Y-%m-%d"),)
)
fp.close()
