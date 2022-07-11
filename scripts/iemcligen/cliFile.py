# WEPP Climate File Class
# Daryl Herzmann 05 Mar 2003

import re, mx.DateTime, cliRecord


class cliFile:
    def __init__(self, hrap_i, s, e):
        self.hrap_i = hrap_i
        self.sts = s
        self.ets = e
        self.bpdata = {}
        self.cldata = {}
        self.sector = -1
        self.days = (e - s).days

    def loadBPData(self):
        o = open("bpdata/%s.dat" % (self.hrap_i,), "r").read()

        tokens = re.split("\[....\....\]\n", o)
        i = 0
        for i in range(self.days):
            ts = self.sts + mx.DateTime.RelativeDateTime(days=+i)
            self.bpdata[ts] = tokens[i + 1]

    def loadCLData(self, cldb):
        for i in range(len(cldb)):
            self.cldata[cldb[i]["day"]] = cldb[i]

    def write(self, fn, header):
        o = open(fn, "w")
        o.write(header)
        now = self.sts
        while now < self.ets:
            clr = cliRecord.cliRecord(now)
            clr.BPset(self.bpdata[now])
            clr.CLset(self.cldata[now.strftime("%Y-%m-%d")])
            clr.write(o)
            now = now + 1
        o.close()
