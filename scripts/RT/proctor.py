"""
"""

import weppRun
import os
import shutil
import sys
import threading
import time
import random
import mx.DateTime
import logging
import pg

wblog = logging.getLogger("wblog")
wblog.setLevel(logging.DEBUG)
fh = logging.FileHandler("wb.log", "w")
fh.setLevel(logging.DEBUG)
wblog.addHandler(fh)

sts = mx.DateTime.DateTime(1997,1,1)
ets = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1,hour=0,minute=0,second=0)

wbfindline = int((ets - sts).days + 20.0)

class WeppThread( threading.Thread ):
    """ I am a processing thread that will do some work """
    chunksize = 1000

    def run( self ):
        self.dbconn = pg.connect('wepp', 'iemdb')
        good = True
        while (good):
            sts = mx.DateTime.now()
            good = self.chunk()
            ets = mx.DateTime.now()
            rt = (ets - sts).seconds
            print "%s Processed %s runs in %.1fs [%.3f runs/s]" % (
              ets.strftime("%H:%M"), self.chunksize, 
              rt, self.chunksize / rt )

    def chunk( self ):
        # First, lets request a request ID from the server
        rs = self.dbconn.query("SELECT \
             nextval('job_queue_request_id'::text) as next").dictresult()
        requestID = rs[0]["next"]

        # Send a request to the server for 1000 combos to make
        self.dbconn.query("UPDATE job_queue SET request_id = %s \
                   WHERE id in (SELECT id from job_queue \
                   WHERE request_id IS NULL LIMIT %s) " % \
                   (requestID, self.chunksize) )

        # Now, ask again for runs that we can make
        sql = "select c.mkrun as mkrun, c.id as cid, c.hrap_i, \
               n.steep, n.len, \
               n.soil_id, c.model_twp, c.nri_id::text as nri_id, \
               n.man_id, m.name FROM \
               combos c, nri n, managements m, job_queue q \
               WHERE q.request_id = %s and q.combo_id = c.id \
               and c.nri_id = n.id and n.man_id = m.man_id" % (requestID)

        rs = self.dbconn.query(sql).dictresult()

        if (len(rs) == 0):
            return False

        for i in range(len(rs)):
            if (rs[i]['mkrun'] == 'f'):
                continue
            runwepp(rs[i])
        return True

def runwepp(row):
    hrap_i = int(row['hrap_i'])
    cid = int(row['cid'])
    wr = weppRun.weppRun(cid)
    wr.model_twp = row['model_twp']
    wr.nri_id = str(row['nri_id'])
    wr.hrap_i = hrap_i
    wr.mfile = row['name']
    if (wr.mfile == "fallow"):
        return
    wr.sid = str(row['soil_id'])
    wr.s_length = row['len']
    wr.s_steep = float(row['steep']) + 0.01

    #wr.buildSlope()
    #wr.buildSoil(mydb)
    wr.buildRun()
    if (wr.error > 0):
        return

    si, so = os.popen4("./wepp < runfiles/wepp.%s" % (cid,))
    r = so.read()
    saveo = open('output/%s.txt'%(cid,),'w')
    saveo.write( r )
    saveo.close()
    if r[-13:-1] != "SUCCESSFULLY":
        e = open('error/%s.txt'%(cid,),'w')
        e.write( r )
        e.close()
        return
    for linenum, line in enumerate(open('wb/%s.wb' % (cid,))):
        if linenum == wbfindline:
            wblog.debug("%s %s" % (cid, line.strip()) )
            break

for x in range(3):
    if x > 0:
        time.sleep( random.random() * 10 ) # Initial jitter
    WeppThread().start()

