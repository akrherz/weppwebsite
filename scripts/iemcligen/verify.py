#!/mesonet/python/bin/python

import os, mx.DateTime

sts = mx.DateTime.DateTime(1997,1,1)
ets = mx.DateTime.DateTime(2006,1,1)
interval = mx.DateTime.RelativeDateTime(days=+1)

files = os.listdir("clifiles")

for filename in files:
    d = {}
    now = sts
    while (now<ets):
        d[now] = 0
        now += interval
    file = open('clifiles/%s'%(filename,), 'r')
    for line in file:
        if (len(line) > 0 and line[0] != " "):
            tokens = line.split()
            if (len(tokens) == 3):
                print filename, line
            if (len(tokens) == 10):
                try:
                    d[ mx.DateTime.DateTime( int(tokens[2]), int(tokens[1]),int(tokens[0])) ] = 1
                except:
                    pass
    for key in d.keys():
        if (d[key] == 0):
            print '%s missing %s' %(filename, key)
