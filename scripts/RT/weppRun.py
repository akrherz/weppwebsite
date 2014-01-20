# Class for Wepp runs
# Daryl Herzmann 5 Mar 2003
# 22 Apr 2003	Fix a stupid text error!!
# 13 May 2003	Don't rebuild input files, if we don't need to...
#		This saves us lots of time!
# 27 May 2003	Slope files being incorrectly built, fix that
# 28 May 2003	Correct the header on the top of the slope file
# 21 Jan 2004	Don't build soil and slope files if we don't haveto

import os

#badSoils = {19035010014: 'f', 19153060014: 'f', 19097080013: 'f'}

class weppRun:
  run_id = None
  model_twp = None
  nri_id = None
  hrap_i = None
  mfile = None
  sid = None
  s_length = None
  s_steep = None
  error = 0

  def __init__(self, cid):
    self.run_id = cid

    # Builds a slope file
  def buildSlope(self):
    slpFile = "slopes/%s.slp" % (self.nri_id,)
    if (os.path.isfile(slpFile)):
      return
    o = open(slpFile, 'w')
    o.write("%s\n%s\n%s %s\n" % (95.7, 1, 0, 100) )
    o.write("2 %6.5f\n" % ( self.s_length * 0.3048 ) )
#    o.write("%5.6f\n" % ( self.s_steep ) )
    o.write("0  %5.6f  1.0  %5.6f\n" % (self.s_steep / 100.00, self.s_steep / 100.00) )

    o.close()

  def buildSoil(self, mydb):
    solFile = "soils/%s.sol" % (self.nri_id,)
    if (os.path.isfile(solFile)):
      return
    o = open(solFile, 'w')
    o.write("%s\n%s\n%s  %s\n" % (97.5, 'NRI Soil File', 1, 1) )
    sql = "SELECT * from soils WHERE \
      soil_id = "+ str(self.sid)
    rs = mydb.query(sql).dictresult()

    try:
      o.write("'%s'  '%s' %s %s %s %s %s %s %s\n" % \
        (rs[0]['name'], rs[0]['texture'], rs[0]['layers'], \
         rs[0]['albedo'], rs[0]['sat'], rs[0]['interrill'], \
         rs[0]['rill'], rs[0]['shear'], rs[0]['conduct']) )
    except:
      print "Missing Soil For NRI: %s , " % (self.nri_id,)
      self.error = 20
      return
    lys = mydb.query("SELECT * from layers \
      WHERE soil_id = "+ str(self.sid) ).dictresult()
    for i in range(len(lys)):
      o.write("%s %s %s %s %s %s\n" % \
       (lys[i]['depth'], lys[i]['sand'], lys[i]['clay'], \
        lys[i]['om'], lys[i]['cec'], lys[i]['rock']) )

    o.close()

  """
             fprintf(fp,"E\n"); // english units
             fprintf(fp,"Yes\n");       // run hillslope
             fprintf(fp,"1\n"); // continuous simulation
             fprintf(fp,"1\n"); // hillslope version
             fprintf(fp,"No\n");        // pass file output?
             fprintf(fp,"1\n"); // abbrv annual output
             fprintf(fp,"No\n");        //  initial conditions output?
             fprintf(fp,"%s\n",outFile);   // soil loss output file
             fprintf(fp,"No\n");        // water balance output?
             fprintf(fp,"No\n");        // crop output?
             fprintf(fp,"No\n");        // soil output?
             fprintf(fp,"No\n");        // distance and sed output?
             fprintf(fp,"No\n");        // large graphics output?
             fprintf(fp,"Yes\n");       // event by event output?
             fprintf(fp,"%s\n",evFile);  // event by event output file
             fprintf(fp,"No\n");        //element output?
             fprintf(fp,"No\n");        // final summary output?
             fprintf(fp,"No\n");        // daily winter output?
             fprintf(fp,"No\n");        // plant yield output?
             fprintf(fp,"%s.man\n",manFile);  // management file
             fprintf(fp,"%s\n",slpFile);    // slope file
             fprintf(fp,"%s\n",cliFile);     // climate file
             fprintf(fp,"%s.sol\n",soilFile);    // soil file
             fprintf(fp,"0\n");         // no irrigation
             fprintf(fp,"%d\n",par->RunYears());   // number of years to run for
             fprintf(fp,"0\n"); // route all events
  """

  def buildRun(self):
    fp = 'runfiles/wepp.%s' % (self.run_id,)
    if os.path.isfile(fp):
      return
    o = open(fp, 'w')
    o.write("""\
E
Yes
1
1
No
1
No
%s
Yes
%s
No
No
No
No
Yes
%s
No
No
No
No
%s
%s
%s
%s
0
%s
0
""" % ("wepp.out", "wb/"+ str(self.run_id)+".wb", "env/"+ str(self.run_id)+".env", \
 "managements/"+ self.mfile+".man", "slopes/"+ str(self.nri_id)+".slp", \
 "clifiles/"+ str(self.hrap_i)+".dat", "soils/"+ str(self.nri_id)+".sol", 17) )
#""" % ("wepp.out", "wb/"+ str(self.run_id)+".wb", "env/"+ str(self.run_id)+".env", \
    o.close()

