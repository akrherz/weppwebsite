# Something to edit Cli Files, not necessarily create them!

import mx.DateTime, sys

class editclifile:

  def __init__(self, filename):
    self.filename = filename
    self.data = open(filename, 'r').read()

  def editDay(self, ts, cliRecord):
    pos0 = self.data.find("%s" % (ts.strftime("%-d\t%-m\t%Y"),) )
    pos1 = self.data.find("%s" % \
   ( (ts + mx.DateTime.RelativeDateTime(days=+1)).strftime("%-d\t%-m\t%Y"),) )

    self.data = self.data[:pos0] + str(cliRecord) + self.data[pos1:]


  def write(self):
    o = open(self.filename, 'w')
    o.write( self.data )
    o.close()

  def editDaySavePrecip(self, ts, cliRecord):
    pos0 = self.data.find("%s" % (ts.strftime("%-d\t%-m\t%Y"),) )
    pos1 = self.data.find("%s" % \
   ( (ts + mx.DateTime.RelativeDateTime(days=+1)).strftime("%-d\t%-m\t%Y"),) )
    ex = (self.data[pos0:pos1]).find("\n")
    s = self.data[pos0+ex:pos1]
    if (len(s) > 3):
      cliRecord.BPset( s[1:] )
    o = open(self.filename, 'w')
    o.write( self.data[:pos0] )
    cliRecord.write(o)
    o.write( self.data[pos1:] )
    o.close()

