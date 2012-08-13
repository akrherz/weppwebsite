#!/mesonet/python/bin/python
# Get solar from ISU AgClimate network and update DB
# Daryl Herzmann 4 Mar 2003
# 2 Jan 2004 Use new isuag database and cleanup

from pyIEM import iemdb
import mx.DateTime, sys
i = iemdb.iemdb()
mydb = i['isuag']
wepp = i['wepp']


cref = {'A138019': 1, 'A134309': 2, 'A135879': 3, 
        'A131299': 4, 'A130209': 5, 'A135849': 6,
        'A134759': 7, 'A131559': 8, 'A131909': 9}

# c80 is solar rad
def process(ts):
  for st in cref.keys():
    tbl = "daily"
    sector = cref[st]
    day = ts.strftime("%Y-%m-%d")
    q = "SELECT c80 from %s WHERE valid = '%s' and station = '%s'" \
      % (tbl, day, st)
    rs = mydb.query(q).dictresult()
    if (len(rs) == 0):
      print "Missing Solar for sector: %s station: %s" % (sector, st)
      continue
    wepp.query("UPDATE climate_sectors SET rad = '"+ str(rs[0]['c80']) +"' \
      WHERE day = '"+ day +"' and sector = "+ str(sector) +" ")

#"""
ts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1)
if (len(sys.argv) == 4):
  ts = mx.DateTime.DateTime( int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
process(ts)
#"""
"""
rs = wepp.query("SELECT distinct(day) as d from climate_sectors WHERE rad < 100 and day > '2012-01-01'").dictresult()
for i in range(len(rs)):
  ts = mx.DateTime.strptime(rs[i]['d'], '%Y-%m-%d')
  print ts
  process( ts )
"""
