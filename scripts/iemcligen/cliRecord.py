# WEEP climate Record Class
# Daryl Herzmann 02 Oct 2002
# 05 Mar 2003	Its alive, its alive!!
# 		bpdata must be over 1 line long

import re, mx.DateTime


class cliRecord:
    def __init__(self, its):
        ba = "Ha"
        self.ts = its
        self.npoints = 0
        self.high = -99  # C
        self.low = -99  # C
        self.rad = 0  # Langleys / Day
        self.wvl = 0  # m/s
        self.wdir = "000"  # Deg
        self.tdew = 0  # C Average Dew Point
        self.lo_c = -99
        self.hi_c = -99
        self.bpdata = ""

    def write(self, out):
        out.write(
            "%s\t%s\t%s\t%s\t%3.1f\t%3.1f\t%4.0f\t%4.1f\t%s\t%4.1f\n%s"
            % (
                self.ts.day,
                self.ts.month,
                self.ts.year,
                self.npoints,
                self.hi_c,
                self.lo_c,
                self.rad,
                self.wvl,
                self.wdir,
                self.dw_c,
                self.bpdata,
            )
        )

    def __str__(self):
        return "%s\t%s\t%s\t%s\t%3.1f\t%3.1f\t%4.0f\t%4.1f\t%s\t%4.1f\n%s" % (
            self.ts.day,
            self.ts.month,
            self.ts.year,
            self.npoints,
            self.hi_c,
            self.lo_c,
            self.rad,
            self.wvl,
            self.wdir,
            self.dw_c,
            self.bpdata,
        )

    def CLset(self, rs):
        if rs["high"] != None:
            self.high = rs["high"]
        else:
            self.high = 100
        if rs["low"] != None:
            self.low = rs["low"]
        else:
            self.low = 100
        if rs["wvl"] != None:
            self.wvl = rs["wvl"]
        if rs["rad"] != None:
            self.rad = rs["rad"]
        if rs["dewp"] != None:
            self.tdew = rs["dewp"]
        else:
            self.tdew = 100
        self.tometric()

    def tometric(self):
        self.hi_c = 5.00 / 9.00 * (self.high - 32.00)
        self.lo_c = 5.00 / 9.00 * (self.low - 32.00)
        self.dw_c = 5.00 / 9.00 * (self.tdew - 32.00)

    def BPset(self, bpdata):
        if len(bpdata) == 0:
            self.npoints = 0
        else:
            self.npoints = len(re.split("\n", bpdata)) - 1
            self.bpdata = bpdata
        if self.npoints == 1:
            self.npoints = 2
            self.bpdata = "00.00       0.00\n" + bpdata


#    else:
#      self.bpdata = bpdata
