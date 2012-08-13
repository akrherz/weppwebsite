#!/mesonet/python/bin/python
# Process the event output files!
# Daryl Herzmann 6 Mar 2003
# 13 May 2003	Need to include an argument to only look for new cases
#  7 Jul 2003	After we insert the data, we need to dump it onto the 
#		aggregate table.
# 23 Sep 2003	We now do a multiplication by the upfact.  Sort of a 
#		big change! :)
# 27 Apr 2004	Remove the group by township stuff

import pg, os, re, mx.DateTime, sys
mydb = pg.connect('wepp', 'iemdb')

upfact = {}
rs = mydb.query("select c.id, n.upfact from combos c, nri n \
  WHERE c.nri_id = n.id").dictresult()
for i in range(len(rs)):
  upfact[ int(rs[i]['id']) ] = rs[i]['upfact']

try:
  year  = int(sys.argv[1])
  month = int(sys.argv[2])
  day   = int(sys.argv[3])
except:
  its = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1)
  year = its.year
  month = its.month
  day = its.day

ots = mx.DateTime.DateTime(year, month, day)

files = os.listdir("env")

fp = open("insert.sql", "w")

fp.write("DELETE from results WHERE valid = '%s';\n" % ( ots.strftime("%Y-%m-%d") ) )
fp.write("COPY results FROM stdin;\n")

j = 0
for file in files:
  run_id = file[:-4]
  o = open("env/"+ file , 'r')
  rowcnt = 0
  for line in o:
    rowcnt += 1
    if (rowcnt < 4): continue
    tokens = re.split("[\s]+", line)
    try:
      ts = mx.DateTime.DateTime(int(tokens[3]) + 1996, int(tokens[2]), int(tokens[1]))
    except:
      print file, tokens
      continue
    if (ts != ots):
      continue
    trunoff = tokens[5]
    tloss = tokens[7]
    tprecip = tokens[4]
    if (j % 1000 == 0 and j != 0):
      fp.write("\.\nCOPY results from STDIN;\n")
    j = j + 1
    fp.write("%s\t%s\t%s\t%5.2f\t%s\n" % (run_id, ts.strftime("%Y-%m-%d"), \
      trunoff, float(tloss) * upfact[int(run_id)] , tprecip))

fp.write("\.\n")
#fp.write("DELETE from results_by_twp WHERE valid = '%s';\n" % (ots.strftime("%Y-%m-%d")) )
#
#fp.write("insert into results_by_twp \
#   (model_twp, valid, min_precip, avg_precip, max_precip, \
#    min_loss, avg_loss, max_loss, min_runoff, avg_runoff, \
#    max_runoff, run_points) \
#       SELECT t.model_twp, '%s', min(r.precip), \
#       avg(r.precip), max(precip), min(loss), avg(loss), max(loss), \
#       min(runoff), avg(runoff), max(runoff), count(precip) \
#       from results r, iatwp t, combos c \
#       WHERE r.valid = '%s' and r.run_id = c.id and \
#       c.model_twp = t.model_twp GROUP by t.model_twp;\n" \
#     % (ots.strftime("%Y-%m-%d"), ots.strftime("%Y-%m-%d") ) )
#
fp.write("DELETE from erosion_log WHERE valid = '%s';\n" % \
	(ots.strftime("%Y-%m-%d"), ) )
fp.write("INSERT into erosion_log (valid) VALUES ('%s'); \n" % \
	(ots.strftime("%Y-%m-%d"), ) )
fp.close()



