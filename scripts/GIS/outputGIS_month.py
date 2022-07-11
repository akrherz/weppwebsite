#!/usr/bin/env python
# Something to generate GIS output of WEPP Runs!
# Daryl Herzmann 2 Apr 2004
# 12 Apr 2004	Fix my db hack. To make things a bit nicer...

import pg, mx.DateTime, sys

weppdb = pg.connect("wepp")
weppdb.query("update iatwp SET truns = 0, eruns = 0, arunoff = 0, aloss = 0")

yyyy = int(sys.argv[1])
mm = int(sys.argv[2])

ts = mx.DateTime.DateTime(yyyy, mm)
ets = ts + mx.DateTime.RelativeDateTime(months=+1)
days = (ets - ts).days


def main():
    # First we load up our combos
    combos = weppdb.query("SELECT id, model_twp from combos").dictresult()
    cDict = {}
    for i in range(len(combos)):
        cDict[int(combos[i]["id"])] = combos[i]["model_twp"]
    del combos

    # Now we need something to keep track of townships:
    twpDict = {}
    for comboid in cDict.keys():
        model_twp = cDict[comboid]
        if not twpDict.has_key(model_twp):
            twpDict[model_twp] = {
                "truns": 0,
                "eruns": 0,
                "trunoff": 0,
                "tloss": 0,
                "arunoff": 0,
                "aloss": 0,
            }
        twpDict[model_twp]["truns"] += days

    # Then we load up our results
    rs = weppdb.query(
        "SELECT * from results WHERE \
		extract(month from valid) = %s and extract(year from valid) = %s \
		"
        % (ts.month, ts.year)
    ).dictresult()

    for i in range(len(rs)):
        comboid = rs[i]["run_id"]
        runoff = rs[i]["runoff"]
        loss = rs[i]["loss"]
        model_twp = cDict[int(comboid)]
        twpDict[model_twp]["eruns"] += 1
        twpDict[model_twp]["trunoff"] += runoff
        twpDict[model_twp]["tloss"] += loss

    # Now we compute the averages
    for model_twp in twpDict.keys():
        twpDict[model_twp]["arunoff"] = twpDict[model_twp]["trunoff"] / float(
            twpDict[model_twp]["truns"]
        )
        twpDict[model_twp]["aloss"] = twpDict[model_twp]["tloss"] / float(
            twpDict[model_twp]["truns"]
        )

        # Need to update the iatwp table
        weppdb.query(
            "UPDATE iatwp SET truns = %s, eruns = %s, arunoff = %s, \
			aloss = %s WHERE model_twp = '%s'"
            % (
                twpDict[model_twp]["truns"],
                twpDict[model_twp]["eruns"],
                twpDict[model_twp]["arunoff"],
                twpDict[model_twp]["aloss"],
                model_twp,
            )
        )


main()
