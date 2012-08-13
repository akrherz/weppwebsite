#!/mesonet/python/bin/python
# Need something to find those hrap polygons missing in the DB

import pg
mydb = pg.connect("wepp")


rs = mydb.query("SELECT hrap_i from hrap_polygons ORDER by hrap_i ASC").dictresult()

last = 0
for i in range(len(rs)):
	t = int(rs[i]["hrap_i"])
	d = t - last
	if (d < 4 and d > 1):
		print t
	last = t
