#!/usr/bin/env python
# Convert a column file into a quick and dirty space seperated values file

import re

o = open('lat_lon_precip_area.txt', 'r').readlines()

lat = open('lats.dat', 'w')
lon = open('lons.dat', 'w')

for i in range(2, len(o)):
  tokens = re.split("[\s+]+", o[i])
  x = int(tokens[0])
  if (x == 1):
    lat.write("\n")
    lon.write("\n")
  lat.write("%2.8f " % (float(tokens[3])) )
  lon.write("%2.8f " % ( float(tokens[2])) )
