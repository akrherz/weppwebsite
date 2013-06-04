#!/mesonet/python/bin/python
# Create the pickled iem_cligen files!
# Daryl Herzmann 6 Jun 2004

import pickle, mx.DateTime, pg, cliFile

s = mx.DateTime.DateTime(1997,1,1)
e = mx.DateTime.DateTime(2005,1,1)

mydb = pg.connect('wepp', 'db1.mesonet.agron.iastate.edu', user='nobody')

cl = {}
# Load up the climate data from the database
cl['NW'] = mydb.query("SELECT * from climate_sectors WHERE sector = 1").dictresult()
cl['NC'] = mydb.query("SELECT * from climate_sectors WHERE sector = 2").dictresult()
cl['NE'] = mydb.query("SELECT * from climate_sectors WHERE sector = 3").dictresult()
cl['WC'] = mydb.query("SELECT * from climate_sectors WHERE sector = 4").dictresult()
cl['C'] = mydb.query("SELECT * from climate_sectors WHERE sector = 5").dictresult()
cl['EC'] = mydb.query("SELECT * from climate_sectors WHERE sector = 6").dictresult()
cl['SW'] = mydb.query("SELECT * from climate_sectors WHERE sector = 7").dictresult()
cl['SC'] = mydb.query("SELECT * from climate_sectors WHERE sector = 8").dictresult()
cl['SE'] = mydb.query("SELECT * from climate_sectors WHERE sector = 9").dictresult()

rs = mydb.query("SELECT mgtzone, hrap_i from hrap_polygons \
        WHERE used = 't'").dictresult()
for i in range(len(rs)):
	hrap_i = rs[i]['hrap_i']
	mgtzone = rs[i]['mgtzone']

	cf = cliFile.cliFile(hrap_i, s, e)
	cf.loadBPData()
	cf.loadCLData(cl[mgtzone])

	pickle.dump(cf, open('clifiles.p/%s.p' % (hrap_i,) , 'w'), bin=1)
