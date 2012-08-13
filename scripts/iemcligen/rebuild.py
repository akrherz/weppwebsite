#!/mesonet/python/bin/python
# I wanna rebuild the climate files, one file at a time! :)
# Daryl Herzmann 5 Apr 2006

import mx.DateTime
from pyIEM import mesonet

import pg, re
mydb = pg.connect('wepp', 'iemdb', user='wepp')

# Load up our climate data
climate = {}
for c in range(1,10):
  climate[c] = {}
rs = mydb.query("SELECT * from climate_sectors").dictresult()
for i in range(len(rs)):
  ts = mx.DateTime.strptime(rs[i]['day'], "%Y-%m-%d")
  climate[ int(rs[i]['sector']) ][ ts ] = rs[i]

# Load up all our cli files
rs = mydb.query("SELECT mgtzone, hrap_i from hrap_polygons \
                WHERE used = 't'").dictresult()

idx = {'NW':1, 'NC':2, 'NE':3, 'WC':4, 'C':5, 'EC':6, 'SW':7, 'SC':8, 'SE':9}

for i in range(len(rs)):
  hrap_i = int(rs[i]['hrap_i'])
  mgtzone = idx[ rs[i]['mgtzone'] ]
  
  o = open('clifiles/%s.dat' % (hrap_i,) )
  out = open('clifiles2/%s.dat' % (hrap_i,), 'w')
  # File read logic
  cnt = -1
  ts = 0
  bpdata = ""
  header = ""
  for line in o:
    cnt += 1
    if (cnt < 16):
      out.write( line)
      continue

    tokens = line.split()
    if (len(tokens) == 10):
      if (ts > 0):
        out.write("%s\t%s\t%s\t%s\t%3.1f\t%3.1f\t%4.0f\t%4.1f\t%s\t%4.1f\n%s"%\
        (ts.day, ts.month, ts.year, bps, hic, \
         loc, srad, wvl, drct, dwpc, bpdata) )

      ts = mx.DateTime.DateTime(int(tokens[2]), int(tokens[1]), int(tokens[0]))
      bps = int(tokens[3])
      hic = mesonet.f2c( float( climate[mgtzone][ts]['high'] ) )
      loc = mesonet.f2c( float( climate[mgtzone][ts]['low'] ) )
      srad = float( climate[mgtzone][ts]['rad'] )
      wvl = float( climate[mgtzone][ts]['wvl'] )
      drct = 0
      dwpc = mesonet.f2c( float( climate[mgtzone][ts]['dewp'] ) )
      bpdata = ""
    elif (len(tokens) == 2):
      bpdata += line

  out.write("%s\t%s\t%s\t%s\t%3.1f\t%3.1f\t%4.0f\t%4.1f\t%s\t%4.1f\n%s"%\
    (ts.day, ts.month, ts.year, bps, hic, \
     loc, srad, wvl, drct, dwpc, bpdata) )
  out.close()

print "FIX 1 Jan 1997!!!"
