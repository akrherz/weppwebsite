#!/mesonet/python/bin/python

import struct

f = open("../test/NCR_20040605_0137.tmp", 'rb').read()

radmode =  struct.unpack('b', f[87])[0]
print "RADAR mode is: %i" % ( radmode,)

#for i in range(len(f)):
#	print struct.unpack('b', f[i])
