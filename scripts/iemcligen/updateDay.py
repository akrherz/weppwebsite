#!/mesonet/python/bin/python
# This script will update the climate DB with new and exciting info!!
# Daryl Herzmann 4 Mar 2003
# 25 Aug 2004	ASOS database moved
# 25 Mar 2005	Don't let sknt be less than zero!
#  5 Apr 2006	Make this thing somewhat intelligent

from pyIEM import iemdb, stationTable
st = stationTable.stationTable("/mesonet/TABLES/iowa.stns")
import mx.DateTime, sys
i = iemdb.iemdb()
mydb = i['wepp']
iemdb = i['iem']
asosdb = i['asos']

ts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1)
if (len(sys.argv) == 4):
  ts = mx.DateTime.DateTime( int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
day = ts.strftime("%Y-%m-%d")


targets = {'SUX': 1, 'MCW': 2, 'DBQ': 3, 
        'DNS': 4, 'DSM': 5, 'CID': 6,
        'ICL': 7, 'LWD': 8, 'BRL': 9}

# Lets find average wind speed, dew point for station
sql = "SELECT avg(sknt) * 2 as wvl from t%s WHERE sknt >= 0 and \
       date(valid) = '%s'" % (ts.year, day)
rs = asosdb.query(sql).dictresult()

wvl = rs[0]['wvl']

for station in targets.keys():
  sql = "SELECT avg(max_tmpf) as high, avg(min_tmpf) as low \
    from summary_%s s, stations t WHERE (t.network ~* 'ASOS' or t.network ~* 'AWOS') \
    and day = '%s' and distance(t.geom, 'SRID=4326;POINT(%s %s)') < 2.5 \
    and max_tmpf > -90 and min_tmpf < 90 and max_dwpf > -90 and min_dwpf < 90\
    and t.iemid = s.iemid\
    " % (ts.year, day, st.sts[station]['lon'], st.sts[station]['lat'])
  
  rs = iemdb.query(sql).dictresult()
  high = rs[0]['high']
  low = rs[0]['low']
  dwpf = (high + low) / 2.0

  sql = "UPDATE climate_sectors SET high = %s, low = %s, wvl = %s,\
     dewp = %s, drct = 0 WHERE sector = %s and day = '%s'" % \
     (high, low, wvl, dwpf, targets[station], day)
  mydb.query(sql)
