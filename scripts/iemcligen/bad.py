#!/mesonet/python/bin/python

import shutil, os

file = open('bad')
d = {}
for line in file:
  f = line.split()[0]
  if (not d.has_key(f)):
    d[f] = 0
  d[f] += 1 

for k in d.keys():
#  if (d[k] > 100):
#    print d[k], k
   q = int(k.split(".")[0]) - 5
   r = int(k.split(".")[0]) + 5

   if (os.path.isfile("clifiles/%s.dat"%(q,))):
      shutil.copy("clifiles/%s.dat"%(q,), "clifiles/%s"%(k,) )
      continue
   if (os.path.isfile("clifiles/%s.dat"%(r,))):
      shutil.copy("clifiles/%s.dat"%(r,), "clifiles/%s"%(k,) )
      continue
   print 'No find: %s' %(q,)
