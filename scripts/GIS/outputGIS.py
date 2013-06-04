#!/mesonet/python/bin/python
# Something to generate GIS output of WEPP Runs!
# Daryl Herzmann 2 Apr 2004
# 12 Apr 2004	Fix my db hack. To make things a bit nicer...

import pg, mx.DateTime, sys
weppdb = pg.connect("wepp")
weppdb.query("update iatwp SET truns = 0, eruns = 0, arunoff = 0, aloss = 0")

yyyy = int(sys.argv[1])
mm = int(sys.argv[2])
dd = int(sys.argv[3])

ts = mx.DateTime.DateTime(yyyy, mm, dd)

def main():
	# First we load up our combos
	combos = weppdb.query("SELECT id, model_twp from combos").dictresult()
	cDict = {}
	for i in range(len(combos)):
		cDict[ int(combos[i]["id"]) ] = combos[i]["model_twp"]
	del(combos)

	# Then we load up our results
	results = weppdb.query("SELECT * from results WHERE \
	valid = '%s' " % (ts.strftime("%Y-%m-%d"),) ).dictresult()
	rDict = {}
	for i in range(len(results)):
		rDict[ int(results[i]["run_id"]) ] = results[i]
	del(results)


	# Now we compute township stuff
	twpDict = {}
	for comboid in cDict.keys():
		model_twp = cDict[comboid]
		if (not twpDict.has_key(model_twp)):
			twpDict[model_twp] = {'truns':0, 'eruns':0, 
			'trunoff':0, 'tloss':0, 'arunoff':0, 'aloss':0}
		if (rDict.has_key(comboid)):
			twpDict[model_twp]['eruns'] += 1
			twpDict[model_twp]['trunoff'] += rDict[comboid]["runoff"]
			twpDict[model_twp]['tloss'] += rDict[comboid]["loss"]
		twpDict[model_twp]['truns'] += 1

	# Now we compute the averages
	for model_twp in twpDict.keys():
		twpDict[model_twp]['arunoff'] = twpDict[model_twp]['trunoff'] / float(twpDict[model_twp]['truns'])
		twpDict[model_twp]['aloss'] = twpDict[model_twp]['tloss'] / float(twpDict[model_twp]['truns'])

		# Need to update the iatwp table
		weppdb.query("UPDATE iatwp SET truns = %s, eruns = %s, arunoff = %s, \
			aloss = %s WHERE model_twp = '%s'" % (twpDict[model_twp]['truns'],\
			twpDict[model_twp]['eruns'], twpDict[model_twp]['arunoff'], \
			twpDict[model_twp]['aloss'], model_twp) )

main()

